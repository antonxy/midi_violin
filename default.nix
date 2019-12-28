let
	pkgs = import <nixpkgs> {};
in pkgs.mkShell rec {
	buildInputs = [
    pkgs.python37
    pkgs.python37Packages.virtualenv
    pkgs.python37Packages.pyserial
    pkgs.python37Packages.evdev
    pkgs.libffi
    pkgs.libjack2
	];
}
