from . import display
from pathlib import Path
import os

from . import operations as ops


class Assembler:

    def __init__(self, os_env, force):
        self.os_env = os_env
        self.force = force

    def install(self):
        display.print_header("Installing Shoestring Assembler...")

        sudo_user = os.getenv("SUDO_USER")
        if sudo_user == "":
            display.print_error(
                "Unable to get user, run 'pipx install shoestring-assembler' once this setup has completed to fix this."
            )
        else:
            ops.subprocess_exec(
                "Installed shoestring assembler",
                ["sudo", "-u", sudo_user, "pipx", "install", "shoestring-assembler"],
            )

            ops.subprocess_exec(
                "Ensured shoestring assembler is latest version",
                ["sudo", "-u", sudo_user, "pipx", "upgrade", "shoestring-assembler"],
            )

            ops.subprocess_exec(
                "Ensured command completions are active",
                ["sudo", "-u", sudo_user, "pipx", "completions"],
            )

            result = ops.logged_subprocess_run(
                ["sudo", "-u", sudo_user, "/bin/sh", "-c", "echo ~"]
            )

            user_home_raw = result.stdout.decode().strip()
            user_home = Path(user_home_raw)

            # Add desktop shortcut to app
            result = ops.logged_subprocess_run(
                ["sudo", "-u", sudo_user, "xdg-user-dir", "DESKTOP"]
            )
            raw_desktop = result.stdout.decode().strip()
            desktop_loc = Path(raw_desktop)

            if desktop_loc.exists():
                display.print_log(f"\[exists]: {desktop_loc}")
                self.create_desktop_shortcut(desktop_loc, user_home, sudo_user)

    def update(self):
        display.print_header("Updating Shoestring Assembler...")

        sudo_user = os.getenv("SUDO_USER")
        if sudo_user == "":
            display.print_error(
                "Unable to get user, run 'pipx upgrade shoestring-assembler' once this setup has completed to fix this."
            )
        else:
            ops.subprocess_exec(
                "Updated shoestring assembler",
                ["sudo", "-u", sudo_user, "pipx", "upgrade", "shoestring-assembler"],
            )

    def create_desktop_shortcut(self, desktop_loc, user_home, sudo_user):
        shoestring_share_dir = user_home / ".local/share/shoestring"
        logo_dest_path = shoestring_share_dir / "shoestring_logo.png"

        desktop_shortcut = f"""
            [Desktop Entry]
            Name=Shoestring Assembler
            Exec={str(user_home / ".local/bin/shoestring")} app
            Comment=shoestring assembler
            Icon={str(logo_dest_path)}
            Type=Application
            Terminal=true
            Encoding=UTF-8
            Categories=Development;
        """.strip()

        import importlib.resources

        logo_src_path = (
            importlib.resources.files("shoestring_setup.assets")
            / "shoestring_logo.png"
        )

        ops.logged_file_write(
            f"{str(desktop_loc)}/shoestring_assembler.desktop",
            mode="w",
            content=desktop_shortcut,
        )  # file permissions should be 644 if needed

        ops.logged_ensure_dir(shoestring_share_dir)
        ops.logged_ensure_owner_group(shoestring_share_dir,sudo_user,sudo_user)

        ops.logged_file_write(
            logo_dest_path, mode="wb", content=logo_src_path.read_bytes()
        )
        ops.logged_ensure_owner_group(logo_dest_path, sudo_user, sudo_user)

        # suppress "execute in shell" pop-up when using shortcut on Pi
        libfm_conf_dir = user_home / ".config/libfm"
        libfm_conf = libfm_conf_dir / "libfm.conf"
        if libfm_conf.exists():
            ops.logged_subprocess_run(
                [
                    "sed",
                    "-i",
                    "s/^quick_exec[\ tab]*=[\ tab]*0[\ tab]*/quick_exec=1/",
                    f"{str(libfm_conf)}",
                ]
            )
        else:
            libfm_global_conf = Path("/etc/xdg/libfm/libfm.conf")
            if libfm_global_conf.exists():
                ops.logged_subprocess_run(
                    [
                        "grep",
                        "-q",
                        "^quick_exec[[:space:]]*=[[:space:]]*.[[:space:]]*$",
                        f"{str(libfm_global_conf)}",
                        "&&",
                        "sed",
                        "-i",
                        "s/^quick_exec[\ tab]*=[\ tab]*0[\ tab]*/quick_exec=1/",
                        f"{str(libfm_global_conf)}",
                        "||",
                        "sed",
                        "-i",
                        "'/^\[config\]/ a\quick_exec=1'",
                        f"{str(libfm_global_conf)}",
                    ]
                )
                ops.logged_ensure_dir(libfm_conf_dir)
                ops.logged_ensure_owner_group(libfm_conf_dir, sudo_user, sudo_user)
                ops.logged_copy(libfm_global_conf, libfm_conf)
                ops.logged_ensure_owner_group(libfm_conf, sudo_user, sudo_user)

        display.print_complete("Created desktop shortcut")
