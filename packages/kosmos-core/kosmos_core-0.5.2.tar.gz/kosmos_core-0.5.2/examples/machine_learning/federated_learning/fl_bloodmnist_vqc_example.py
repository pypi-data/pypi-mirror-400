import torch

from kosmos.circuit_runner.pennylane_runner import PennyLaneRunner
from kosmos.ml.config.factories.encoding import AmplitudeEmbeddingConfig
from kosmos.ml.config.factories.loss import CrossEntropyLossConfig
from kosmos.ml.config.factories.model import VQCConfig
from kosmos.ml.config.factories.optimizer import AdamOptimizerConfig
from kosmos.ml.config.sl_train import FLTrainConfig
from kosmos.ml.datasets.bloodmnist_dataset import BloodMNISTDataset
from kosmos.simulator.fl_simulator import FLSimulator
from kosmos.topology.predefined_quantum.factory import create_topology


def fl_bloodmnist_vqc_example() -> None:
    """Run example of federated training and testing on the BloodMNIST dataset using a VQC."""
    network = create_topology("ring", 3)  # Create a ring topology with 3 nodes
    nodes_list = list(network.nodes())
    server_node = nodes_list[0]  # Use the first node as the server node
    client_nodes = nodes_list[1:]  # All other nodes are clients

    # Dataset to train and test on
    dataset = BloodMNISTDataset()

    # Model configuration that defines the variational quantum circuit to use
    vqc_config = VQCConfig(
        circuit_runner=PennyLaneRunner(),
        num_layers=2,
        encoding_config=AmplitudeEmbeddingConfig(),
        weight_mapping_func=lambda x: torch.pi * torch.tanh(x),
        input_mapping_func=lambda x: torch.pi * x,
        weight_init_range=(-1, 1),
        bias_init_range=(-0.001, 0.001),
        data_reuploading=True,
        output_scaling=True,
    )

    # Configure federated learning
    train_config = FLTrainConfig(
        dataset=dataset,
        train_split=0.7,
        batch_size=128,
        num_epochs=5,
        model_config=vqc_config,
        optimizer_config=AdamOptimizerConfig(lr=1e-3),
        lr_scheduler_config=None,
        max_grad_norm=1.0,
        loss_config=CrossEntropyLossConfig(),
        num_rounds=5,
    )

    # Initialize simulator, which is responsible for running the federated learning experiment
    simulator = FLSimulator(
        network,
        train_config,
        client_nodes=client_nodes,
        server_node=server_node,
        seed=1,
    )

    # Run training
    for epoch_result in simulator.train():
        print(epoch_result)  # noqa: T201

    # Evaluate trained model
    print(simulator.test())  # noqa: T201


if __name__ == "__main__":
    fl_bloodmnist_vqc_example()
