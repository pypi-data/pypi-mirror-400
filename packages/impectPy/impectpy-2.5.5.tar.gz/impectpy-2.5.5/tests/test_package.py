# load packages
import sys
import importlib
import logging
import os
import re
import subprocess
from pathlib import Path
from tqdm import tqdm
from dotenv import load_dotenv
import pandas as pd

execute_functions = False

# branch comparison configuration
BRANCH_A_NAME = "139-playercountry-showing-nan-only"
BRANCH_B_NAME = "release"

REPO_ROOT = Path(__file__).resolve().parents[1]
BRANCH_PATHS = {
    BRANCH_A_NAME: REPO_ROOT,
    BRANCH_B_NAME: REPO_ROOT,
}


def checkout_branch(branch_name: str):
    repo_path = BRANCH_PATHS.get(branch_name)
    if repo_path is None or not repo_path.exists():
        raise ValueError(f"Unknown branch or missing repo path: '{branch_name}'")

    try:
        subprocess.run(
            ["git", "-C", str(repo_path), "fetch"],
            check=True,
            stdout=subprocess.DEVNULL
        )
        subprocess.run(
            ["git", "-C", str(repo_path), "checkout", branch_name],
            check=True,
            stdout=subprocess.DEVNULL
        )
    except subprocess.CalledProcessError as e:
        print(f"Error checking out branch '{branch_name}' in {repo_path}: {e}")


def load_impect(env: str):
    modules_to_remove = [m for m in sys.modules if m.startswith("impectPy")]

    for module_name in modules_to_remove:
        del sys.modules[module_name]

    sys.path = [p for p in sys.path if "impectPy" not in p]

    importlib.invalidate_caches()

    repo_root = BRANCH_PATHS.get(env)
    if repo_root is None:
        raise ValueError(f"Unknown environment '{env}'. Check BRANCH_PATHS.")

    sys.path.insert(0, str(repo_root))
    return importlib.import_module("impectPy")

if execute_functions:

    # define login credentials
    load_dotenv()
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")

    # define logger
    logging.basicConfig(
        level=logging.ERROR,
        format="%(asctime)s - %(name)s - %(levelname)s - ID=%(id)s - URL=%(url)s - %(message)s"
    )

    # define object to be passed onto functions
    iteration = 1385

    matches = [
        232434,
        202485
    ]

    positions = [
        "GOALKEEPER",
        "LEFT_WINGBACK_DEFENDER",
        "RIGHT_WINGBACK_DEFENDER",
        "CENTRAL_DEFENDER",
        "DEFENSE_MIDFIELD",
        "CENTRAL_MIDFIELD",
        "ATTACKING_MIDFIELD",
        "LEFT_WINGER",
        "RIGHT_WINGER",
        "CENTER_FORWARD"
    ]

    # define branches
    branches = [BRANCH_A_NAME, BRANCH_B_NAME]

    # iterate over envs
    for branch in branches:

        os.makedirs(f"files/{branch}", exist_ok=True)

        checkout_branch(branch)
        impectPy = load_impect(branch)
        print(f"impectPy Version: {impectPy.__version__}")

        config = impectPy.Config()
        api = impectPy.Impect(config=config)
        api.login(username, password)

        with tqdm(total=20, desc=f"{branch}: Executing functions...", unit="chunk") as pbar:

            # get iterations
            iterations = api.getIterations()
            iterations.to_csv(f"files/{branch}/iterations.csv")
            pbar.update()

            # get squad ratings
            ratings = api.getSquadRatings(iteration)
            ratings.to_csv(f"files/{branch}/ratings.csv")
            pbar.update()

            # get squad coefficients
            coefficients = api.getSquadCoefficients(iteration)
            coefficients.to_csv(f"files/{branch}/coefficients.csv")
            pbar.update()

            # get matches
            matchplan = api.getMatches(iteration)
            matchplan.to_csv(f"files/{branch}/matchplan.csv")
            pbar.update()

            # get match info
            formations = api.getFormations(matches)
            formations.to_csv(f"files/{branch}/formations.csv")
            pbar.update()
            substitutions = api.getSubstitutions(matches)
            substitutions.to_csv(f"files/{branch}/substitutions.csv")
            pbar.update()
            startingPositions = api.getStartingPositions(matches)
            startingPositions.to_csv(f"files/{branch}/startingPositions.csv")
            pbar.update()

            # get match events
            events = api.getEvents(matches, include_kpis=True, include_set_pieces=True)
            events.to_csv(f"files/{branch}/events.csv")
            pbar.update()

            # get set pieces
            set_pieces = api.getSetPieces(matches)
            set_pieces.to_csv(f"files/{branch}/set_pieces.csv")
            pbar.update()

            # get player iteration averages
            playerIterationAverages = api.getPlayerIterationAverages(iteration)
            playerIterationAverages.to_csv(f"files/{branch}/playerIterationAverages.csv")
            pbar.update()

            # get player matchsums
            playerMatchsums = api.getPlayerMatchsums(matches)
            playerMatchsums.to_csv(f"files/{branch}/playerMatchsums.csv")
            pbar.update()

            # get squad iteration averages
            squadIterationAverages = api.getSquadIterationAverages(iteration)
            squadIterationAverages.to_csv(f"files/{branch}/squadIterationAverages.csv")
            pbar.update()

            # get squad matchsums
            squadMatchsums = api.getSquadMatchsums(matches)
            squadMatchsums.to_csv(f"files/{branch}/squadMatchsums.csv")
            pbar.update()

            # get player match scores
            playerMatchScores = api.getPlayerMatchScores(matches)
            playerMatchScores.to_csv(f"files/{branch}/playerMatchScores.csv")
            pbar.update()
            playerMatchScores_2 = api.getPlayerMatchScores(matches, positions)
            playerMatchScores_2.to_csv(f"files/{branch}/playerMatchScores_2.csv")
            pbar.update()

            # get squad match scores
            squadMatchScores = api.getSquadMatchScores(matches)
            squadMatchScores.to_csv(f"files/{branch}/squadMatchScores.csv")
            pbar.update()

            # get player iteration scores
            playerIterationScores = api.getPlayerIterationScores(iteration)
            playerIterationScores.to_csv(f"files/{branch}/playerIterationScores.csv")
            pbar.update()
            playerIterationScores_2 = api.getPlayerIterationScores(iteration, positions)
            playerIterationScores_2.to_csv(f"files/{branch}/playerIterationScores_2.csv")
            pbar.update()

            # get squad iteration scores
            squadIterationScores = api.getSquadIterationScores(iteration)
            squadIterationScores.to_csv(f"files/{branch}/squadIterationScores.csv")
            pbar.update()

            # get player profile scores
            playerProfileScores = api.getPlayerProfileScores(iteration, positions)
            playerProfileScores.to_csv(f"files/{branch}/playerProfileScores.csv")
            pbar.update()

print("\nRunning auto-diff between source and test outputs...\n")

base_path = Path(__file__).parent / "files"
source_path = base_path / BRANCH_A_NAME
test_path = base_path / BRANCH_B_NAME

excluded_columns = [
    # "playerCountry"
]

failed = False
assertion_error_patterns = {
    "column": re.compile(r'column name="([^"]+)"'),
    "percentage": re.compile(r'values are different \(([\d.]+)\s*%\)'),
    "first_diff": re.compile(
        r'At positional index (\d+), first diff:\s*(.*?)\s*!=\s*(.*)'
    ),
}

for src_file in source_path.glob("*.csv"):
    test_file = test_path / src_file.name

    if not test_file.exists():
        print(f"[MISSING] {src_file.name} not found in test/")
        failed = True
        continue

    src_df = pd.read_csv(src_file, low_memory=False)
    test_df = pd.read_csv(test_file, low_memory=False)

    src_df = src_df[[col for col in src_df.columns if col not in excluded_columns]]
    test_df = test_df[[col for col in test_df.columns if col not in excluded_columns]]

    try:
        pd.testing.assert_frame_equal(
            src_df,
            test_df,
            check_dtype=False,
            check_like=True
        )
        print(f"[OK] {src_file.name}")
    except AssertionError as e:
        parsed_error = str(e)

        column = assertion_error_patterns["column"].search(parsed_error).group(1)
        percentage = float(assertion_error_patterns["percentage"].search(parsed_error).group(1))

        first_diff_match = assertion_error_patterns["first_diff"].search(parsed_error)
        first_diff = {
            "index": int(first_diff_match.group(1)),
            "left": first_diff_match.group(2),
            "right": first_diff_match.group(3),
        }

        result = {
            "column": column,
            "percentage_diff": percentage,
            "first_diff": first_diff,
        }

        print(f"[DIFF] {src_file.name} : Column '{result['column']}‘ (Delta: {result['percentage_diff']:.2f}%)') : "
              f"First Diff at index {result['first_diff']['index']} "
              f"({result['first_diff']['left']} != {result['first_diff']['right']})")
        failed = True

if failed:
    raise AssertionError("Auto-diff failed: source and test outputs differ")

print("\nAll source vs test outputs are identical ✅")