import matplotlib.pyplot as plt
import numpy as np


def plot_risk_surface(
    surface: np.ndarray,
    title: str = "Flood Risk Surface",
    cmap: str = "viridis",
):
    """
    Visualize a single flood-risk surface.
    """
    plt.figure(figsize=(6, 6))
    plt.imshow(surface, cmap=cmap)
    plt.colorbar(label="Flood Risk")
    plt.title(title)
    plt.axis("off")
    plt.tight_layout()
    plt.show()


def compare_risk_surfaces(
    reference: np.ndarray,
    synthetic: np.ndarray,
):
    """
    Side-by-side comparison of reference vs synthetic flood risk.
    """
    fig, axes = plt.subplots(1, 2, figsize=(10, 5))

    im0 = axes[0].imshow(reference, cmap="viridis")
    axes[0].set_title("Reference")
    axes[0].axis("off")

    im1 = axes[1].imshow(synthetic, cmap="viridis")
    axes[1].set_title("Synthetic")
    axes[1].axis("off")

    fig.colorbar(im1, ax=axes, fraction=0.046)
    plt.tight_layout()
    plt.show()
