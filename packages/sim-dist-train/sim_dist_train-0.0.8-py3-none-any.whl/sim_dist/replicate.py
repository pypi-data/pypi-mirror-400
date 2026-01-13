from pydantic import BaseModel
from torch import nn
from typing import Dict, List, Tuple
from loguru import logger
import torch
from torch.func import vmap, functional_call


class ParamMeta(BaseModel):
    name: str
    offset: int
    size: int
    aligned_size: int
    wd: bool = False


class ReplicatedModel(nn.Module):
    def __init__(
        self,
        base_model: nn.Module,
        num_replicas: int,
        exclude_wd_keys: list[str] = ["bn", "bias"],
    ):
        super(ReplicatedModel, self).__init__()
        assert torch.cuda.is_available(), "ReplicatedModel requires CUDA."

        # for numerical stability
        torch.backends.cuda.matmul.allow_tf32 = False
        torch.backends.cudnn.allow_tf32 = False

        self._base_model = base_model.cuda()
        self._num_replicas = num_replicas
        self._exclude_wd_keys = exclude_wd_keys

        self._param_keys = [n for n, _ in self._base_model.named_parameters()]
        self._create_param_buckets()

    def _create_param_buckets(self):
        wd_total_size = 0
        non_wd_total_size = 0
        params = [(n, p) for n, p in self._base_model.named_parameters()]
        self._meta: Dict[str, ParamMeta] = {}

        for n, p in params:
            aligned_size = self._align(p.numel())

            if any(key in n for key in self._exclude_wd_keys):
                wd = False
                offset = non_wd_total_size
                non_wd_total_size += aligned_size
            else:
                wd = True
                offset = wd_total_size
                wd_total_size += aligned_size

            self._meta[n] = ParamMeta(
                name=n,
                offset=offset,
                size=p.numel(),
                aligned_size=aligned_size,
                wd=wd,
            )

        logger.debug(f"Total wd param size: {wd_total_size}")
        logger.debug(f"Total non-wd param size: {non_wd_total_size}")
        logger.debug(f"Number of replicas: {self._num_replicas}")
        logger.debug(
            f"Padding wd param size: {wd_total_size - sum(m.size for m in self._meta.values() if m.wd)}"
        )
        logger.debug(
            f"Padding non-wd param size: {non_wd_total_size - sum(m.size for m in self._meta.values() if not m.wd)}"
        )

        self._wd_bucket = torch.zeros(
            (self._num_replicas, wd_total_size), device="cuda"
        ).requires_grad_(True)
        self._non_wd_bucket = torch.zeros(
            (self._num_replicas, non_wd_total_size), device="cuda"
        ).requires_grad_(True)
        self._base_wd_bucket = torch.zeros((wd_total_size,), device="cuda")
        self._base_non_wd_bucket = torch.zeros((non_wd_total_size,), device="cuda")

        self._wd_bucket_grad = torch.zeros_like(self._wd_bucket)
        self._non_wd_bucket_grad = torch.zeros_like(self._non_wd_bucket)
        self._wd_bucket.grad = self._wd_bucket_grad
        self._non_wd_bucket.grad = self._non_wd_bucket_grad

        self._param_dict: Dict[str, torch.Tensor] = {}
        for n, p in params:
            meta = self._meta[n]
            # map parameter from the base model to its corresponding bucket
            bucket = self._base_wd_bucket if meta.wd else self._base_non_wd_bucket
            param_view = bucket[meta.offset : meta.offset + meta.size].view(*p.shape)
            param_view.data.copy_(p.data)
            p.data = param_view

            # map replicated parameters to their corresponding buckets
            bucket = self._wd_bucket if meta.wd else self._non_wd_bucket
            grad_bucket = self._wd_bucket_grad if meta.wd else self._non_wd_bucket_grad
            param_view = bucket[:, meta.offset : meta.offset + meta.size].view(
                self._num_replicas, *p.shape
            )
            param_view.data.copy_(p.data.unsqueeze(0))
            param_view.grad = grad_bucket[
                :, meta.offset : meta.offset + meta.size
            ].view(self._num_replicas, *p.shape)
            self._param_dict[n] = param_view

        self._buffer_dict: Dict[str, torch.Tensor] = {}
        for n, b in self._base_model.named_buffers():
            self._buffer_dict[n] = (
                torch.zeros_like(b, device="cuda")
                .view(1, *b.shape)
                .tile(self._num_replicas, *((1,) * len(b.shape)))
            )
            self._buffer_dict[n].data.copy_(b.data.unsqueeze(0))

    def get_params(self) -> List[Tuple[str, torch.Tensor]]:
        return [("wd_bucket", self._wd_bucket), ("others", self._non_wd_bucket)]

    @torch.no_grad()
    def compute_loss(
        self,
        inputs: torch.Tensor,
        targets: torch.Tensor,
        criterion: torch.nn.Module,
        train: bool = True,
    ) -> torch.Tensor:
        self._base_model.train(train)
        losses = vmap(
            lambda params, buffers, x, y: criterion(
                functional_call(self._base_model, params | buffers, (x,), strict=True),
                y,
            ),
            in_dims=(0, 0, 0, 0),
        )(self._param_dict, self._buffer_dict, inputs, targets)
        return losses

    @torch.no_grad()
    def compute_grad(
        self,
        inputs: torch.Tensor,
        targets: torch.Tensor,
        criterion: torch.nn.Module,
        train: bool = True,
    ) -> torch.Tensor:
        self._base_model.train(train)

        def loss_fn(params, buffers, input, target):
            logit = functional_call(
                self._base_model, params | buffers, (input,), strict=True
            )
            loss = criterion(logit, target)
            return loss, loss

        grads, losses = vmap(
            torch.func.grad(loss_fn, has_aux=True),
            in_dims=(0, 0, 0, 0),
        )(self._param_dict, self._buffer_dict, inputs, targets)

        target_grads = []

        for n, g in grads.items():
            if self._meta[n].wd:
                grad = self._wd_bucket_grad[
                    :,
                    self._meta[n].offset : self._meta[n].offset + self._meta[n].size,
                ].view_as(g)
                assert grad.is_shared()
            else:
                grad = self._non_wd_bucket_grad[
                    :,
                    self._meta[n].offset : self._meta[n].offset + self._meta[n].size,
                ].view_as(g)
                assert grad.is_shared()
            target_grads.append(grad)
        torch._foreach_copy_(target_grads, [g for _, g in grads.items()])

        return losses

    @torch.no_grad()
    def compute_hvp_along_with_grad(
        self,
        inputs: torch.Tensor,
        targets: torch.Tensor,
        criterion: torch.nn.Module,
        vector: torch.Tensor,
        train: bool = True,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        self._base_model.train(train)

        def _compute_loss_fn(param_dict, buffer_dict, inputs, targets):
            loss = criterion(
                functional_call(
                    self._base_model, param_dict | buffer_dict, (inputs,), strict=True
                ),
                targets,
            )
            return loss, loss

        def _compute_grad_fn(param_dict, buffer_dict, inputs, targets):
            return torch.func.grad(_compute_loss_fn, has_aux=True)(
                param_dict, buffer_dict, inputs, targets
            )

        def _compute_grad_dot_v_fn(param_dict, buffer_dict, inputs, targets, vector):
            grad, loss = _compute_grad_fn(param_dict, buffer_dict, inputs, targets)

            grad_list = [grad[n] for n in self._param_keys]
            grad_dot_v = torch.dot(
                torch.cat([g.contiguous().view(-1) for g in grad_list]), vector
            )
            return grad_dot_v, (grad, loss)

        hvp, (grads, losses) = vmap(
            torch.func.grad(_compute_grad_dot_v_fn, has_aux=True),
            in_dims=(0, 0, 0, 0, 0),
            chunk_size=None,
        )(self._param_dict, self._buffer_dict, inputs, targets, vector)

        target_grads = []
        for n, g in grads.items():
            if self._meta[n].wd:
                grad = self._wd_bucket_grad[
                    :,
                    self._meta[n].offset : self._meta[n].offset + self._meta[n].size,
                ].view_as(g)
                assert grad.is_shared()
            else:
                grad = self._non_wd_bucket_grad[
                    :,
                    self._meta[n].offset : self._meta[n].offset + self._meta[n].size,
                ].view_as(g)
                assert grad.is_shared()
            target_grads.append(grad)
        torch._foreach_copy_(target_grads, [g.contiguous() for _, g in grads.items()])

        concat_hvp = torch.cat([hvp[n].contiguous().view(self._num_replicas, -1) for n in self._param_keys], dim=1)
        return concat_hvp, losses

    def zero_grad(self, set_to_none: bool = False):
        self._wd_bucket_grad.zero_()
        self._non_wd_bucket_grad.zero_()

    @torch.no_grad()
    def mix(self, mix_matrix: torch.Tensor, is_sparse: bool = False):
        if is_sparse:
            output = torch.sparse.mm(mix_matrix, self._wd_bucket)
            self._wd_bucket.copy_(output)
            output = torch.sparse.mm(mix_matrix, self._non_wd_bucket)
            self._non_wd_bucket.copy_(output)
        else:
            self._wd_bucket.copy_(mix_matrix @ self._wd_bucket)
            self._non_wd_bucket.copy_(mix_matrix @ self._non_wd_bucket)

    @torch.no_grad()
    def global_avg(self):
        self._base_wd_bucket.copy_(self._wd_bucket.mean(dim=0))
        self._base_non_wd_bucket.copy_(self._non_wd_bucket.mean(dim=0))

    def _align(self, size: int):
        return ((size + 31) // 32) * 32


if __name__ == "__main__":
    from sim_dist.models import get_model, Model
    from sim_dist.data import CifarLoader, Dataset

    torch.manual_seed(42)
    torch.cuda.manual_seed(42)
    # torch.backends.cudnn.deterministic = True
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False

    world_size = 8

    loader = CifarLoader(
        ds_name=Dataset.CIFAR10,
        data_path="./data",
        train=True,
        batch_size=128,
        num_replicas=world_size,
        base_seed=42,
    )

    base = get_model(Model.WRN_16_10, num_classes=10)
    model = ReplicatedModel(base, num_replicas=world_size)

    mix_matrices = [
        torch.zeros((world_size, world_size), device="cuda") for _ in range(2)
    ]
    for i in range(world_size):
        mix_matrices[0][i, i] = 0.5
        mix_matrices[1][i, i] = 0.5
        if i % 2 == 0:
            mix_matrices[0][i, (i - 1 + world_size) % world_size] = 0.5
            mix_matrices[1][i, (i + 1) % world_size] = 0.5
        else:
            mix_matrices[0][i, (i + 1) % world_size] = 0.5
            mix_matrices[1][i, (i - 1 + world_size) % world_size] = 0.5

    num_params = sum(p.numel() for p in base.parameters())
    vector = torch.randn((world_size, num_params), device="cuda")

    # mix_matrices = [x.to_sparse_csr() for x in mix_matrices]

    with torch.profiler.profile(
        schedule=torch.profiler.schedule(wait=5, warmup=10, active=4, repeat=1),
        on_trace_ready=torch.profiler.tensorboard_trace_handler(
            "./logs/replicated_model"
        ),
        activities=[
            torch.profiler.ProfilerActivity.CPU,
            torch.profiler.ProfilerActivity.CUDA,
        ],
    ) as profiler:
        for data, label in loader:
            # loss = model.compute_loss(data, label, nn.CrossEntropyLoss())
            with torch.autograd.profiler.record_function("zero_grad"):
                model.zero_grad()
            with torch.autograd.profiler.record_function("forward_backward"):
                loss1 = model.compute_loss(data, label, nn.CrossEntropyLoss())
                loss2 = model.compute_grad(data, label, nn.CrossEntropyLoss())
                hvp, loss3 = model.compute_hvp_along_with_grad(
                    data, label, nn.CrossEntropyLoss(), vector
                )

            with torch.autograd.profiler.record_function("mix"):
                model.mix(mix_matrices[0], is_sparse=False)
                model.global_avg()
            # profiler.step()
            print(loss1, loss2, loss3)
            print(torch.cuda.max_memory_allocated() / 1024**2)

            exit(0)
