from pathlib import Path
import limr

data_dir = Path(limr.__file__).parent / "data"

PROD_MODEL_BASE_DIR = data_dir / "prod_model"
TEST_MODEL_BASE_DIR = data_dir / "test_model"

PROD_MODEL_MAP = {
    'late-inspiral':PROD_MODEL_BASE_DIR/"20260106_pofh_gp_inspiral_model",
    'merger':PROD_MODEL_BASE_DIR/"20260106_pofh_gp_model",
    'remnant':PROD_MODEL_BASE_DIR/"20251109_remnant_model",
}

TEST_MODEL_MAP = {
    'late-inspiral':TEST_MODEL_BASE_DIR/"20251109_pofh_gp_model_inspiral_model_B",
    'merger':TEST_MODEL_BASE_DIR/"20251109_pofh_gp_model_B",
    'remnant':TEST_MODEL_BASE_DIR/"20251109_remnant_model_B",
}