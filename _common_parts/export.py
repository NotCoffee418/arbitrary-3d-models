from build123d import export_step
from build123d.mesher import Mesher
from pathlib import Path


def export_model(part, name: str):
    """
    Export a build123d part to STEP, STL, and 3MF in current directory.
    Works in Jupyter notebooks.

    Args:
        part: The build123d part to export
        name: Filename without extension
    """
    # In Jupyter, Path.cwd() gives you the notebook's directory
    export_dir = Path.cwd()

    # Export STEP
    step_path = export_dir / f"{name}.step"
    export_step(part, str(step_path))
    print(f"Exported STEP: {step_path}")

    # Create mesher for STL and 3MF
    mesher = Mesher()
    mesher.add_shape(part)

    # Export STL
    stl_path = export_dir / f"{name}.stl"
    mesher.write(str(stl_path))
    print(f"Exported STL: {stl_path}")

    # Export 3MF
    mf3_path = export_dir / f"{name}.3mf"
    mesher.write(str(mf3_path))
    print(f"Exported 3MF: {mf3_path}")
