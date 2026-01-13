import argparse
import os
import subprocess
import sys
from pathlib import Path

import toml
from colorama import just_fix_windows_console
from termcolor import colored
import semantic_version as SemVer

just_fix_windows_console()

python_cmd = "py" if os.name == "nt" else "python3"
pyproject_path = Path("pyproject.toml")
purples = {
    "1": (95, 2, 130),
    "2": (136, 3, 186),
    "3": (161, 11, 190),
}


def log_step(text: str, color=purples["1"]):
    print("-" * len(text))
    print(colored(text, color))
    print("-" * len(text))


def _run(args: list[str], error_msg: str = None):
    exit_code = subprocess.run(args).returncode
    if exit_code != 0:
        raise Exception(f"{error_msg if error_msg else f'Falha ao executar: {args}'}")


def get_toml_file():
    if not pyproject_path.is_file():
        print(f"{colored('pyproject.toml', purples['1'])} não encontrado.")
        sys.exit(1)

    return toml.load(pyproject_path)

def get_new_version(provided_version: str | None, tipo: str) -> str:
    if provided_version is not None:
        return provided_version

    pyproject = get_toml_file()
    current_version = pyproject["project"]["version"]
    semver = SemVer.Version(current_version)

    if tipo == "major":
        new_version = f"{semver.major + 1}.0.0"
    elif tipo == "minor":
        new_version = f"{semver.major}.{semver.minor + 1}.0"
    else:  # patch
        new_version = f"{semver.major}.{semver.minor}.{semver.patch + 1}"

    return new_version

# Function to validate the version using semantic_version and prompt the user for confirmation
def confirm_new_version(pyproject, new_version):
    old_version = pyproject["project"]["version"]

    c_old_version = colored(old_version, purples["1"], attrs=["bold"])
    c_version = colored(new_version, purples["2"], attrs=["bold"])

    print(f"Versão atual: {c_old_version}")
    print(f"Versão nova: {c_version}")

    # lança  erro se a string de versão for inválida
    new_v = SemVer.Version(new_version)
    old_v = SemVer.Version(old_version)

    if new_v == old_v:
        raise Exception("A nova versão é igual à atual")
    if new_v < old_v:
        raise Exception("A nova versão é anterior à atual")

    confirmation = input(
        f"Confirma a alteração de versão de {c_old_version} para {c_version}? (S/n): "
    )

    return confirmation.lower() == "s" or not confirmation


# Function to update the version in pyproject.toml
def update_version_in_toml(pyproject, version: str):
    pyproject["project"]["version"] = version
    toml.dump(pyproject, open(pyproject_path, "w", encoding="utf-8"))


# Function to check for uncommitted changes
def check_git_status():
    status = subprocess.run(
        ["git", "status", "--porcelain"], capture_output=True, text=True
    )
    if status.stdout.strip():
        raise Exception(
            colored(
                "Você tem alterações no git. Verifique e faça commit antes de fazer upload.",
                purples["2"],
            )
        )


# Function to create a new git tag
def create_git_tag(version):
    _run(["git", "add", "."])
    _run(["git", "commit", "-m", f"chore: v{version}"])
    subprocess.run(["git", "tag", version], stderr=subprocess.DEVNULL)


# function to push the tag to origin
def push_git(version):
    _run(["git", "push", "origin", version])
    _run(["git", "push"])


# function to reset git changes
def reset_git(version, created_git_tag: bool, changed_files: bool):
    if not create_git_tag or not changed_files:
        return

    log_step("Resetando alterações no git", "red")
    if created_git_tag:
        subprocess.run(["git", "tag", "-d", version], stderr=subprocess.DEVNULL)

    if changed_files:
        subprocess.run(["git", "checkout", "."])


# Function to build the package
def build_package():
    _run([python_cmd, "-m", "build"], "Erro ao realizar build")


# Function to upload the package
def upload_package(version: str):
    _run(
        [python_cmd, "-m", "twine", "upload", f"dist/*{version}*"],
        "Erro ao realizar upload",
    )


# Main functionality
def main():
    parser = argparse.ArgumentParser(
        description="Faz build e upload do módulo para o Pypi"
    )
    parser.add_argument(
        "version",
        help="Nova versão do módulo. Se omitida, irá subir uma versão de patch (adiciona 1 ao último número, ex.: 1.2.3 -> 1.2.4).",
        nargs="?",
        default=None,
    )
    parser.add_argument(
        "-t",
        "--tipo",
        type=str,
        choices=["major", "minor", "patch"],
        help="""Tipo de versão a ser incrementada automaticamente, caso a versão não seja especificada.
            Opções: major, minor, patch. Default: patch. Saiba mais: https://semver.org/""",
        default="patch",
    )
    parser.add_argument(
        "-b",
        "--build",
        action="store_false",
        help="Passar esse argumento desabilita o build.",
        default=True,
    )
    parser.add_argument(
        "-u",
        "--upload",
        action="store_false",
        help="Passar esse argumento desabilita o upload.",
        default=True,
    )
    args = parser.parse_args()
    version = get_new_version(args.version, args.tipo)

    created_git_tag = False
    changed_files = False
    try:
        check_git_status()

        pyproject = get_toml_file()

        log_step("Validando versão")
        if not confirm_new_version(pyproject, version):
            print("Operação abortada")
            sys.exit()

        log_step("Atualizando versão no pyproject.toml")
        update_version_in_toml(pyproject, version)
        changed_files = True

        if args.build:
            log_step("Realizando build")
            build_package()
        else:
            log_step("Pulando build")

        if args.upload:
            log_step("Realizando upload")
            upload_package(version)
        else:
            log_step("Pulando upload")

        log_step("Fazendo commit das alterações e criando tag no git")
        create_git_tag(version)
        created_git_tag = True
        if args.upload:
            log_step("Subindo tag no git")
            push_git(version)
        else:
            log_step("Pulando push no git")

        print()
        print(
            colored(
                "*** Sucesso! ***", color="white", on_color=purples["3"], attrs=["bold"]
            ),
        )
    except KeyboardInterrupt:
        print(colored("Encerrando por escolha do usuárie. Tchau!", purples["3"]))
        reset_git(version, created_git_tag, changed_files)
        sys.exit()
    except Exception as e:
        print(f"{colored('Erro:', 'red', attrs=['bold'])} {e}")
        reset_git(version, created_git_tag, changed_files)


if __name__ == "__main__":
    main()
