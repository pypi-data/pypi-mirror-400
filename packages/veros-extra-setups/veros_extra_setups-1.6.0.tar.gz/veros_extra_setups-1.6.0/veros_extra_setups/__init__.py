import warnings

try:
    from veros import __version__ as veros_version
except ImportError as exc:
    raise RuntimeError(
        'veros-extra-setups needs Veros to be installed (try `pip install veros`)'
    ) from exc

from . import _version
__version__ = _version.get_versions()['version']


def _sanitize_version(version):
    parts = version.split("+")
    return parts[0]


this_version = _sanitize_version(__version__)
veros_version = _sanitize_version(veros_version)

if this_version != veros_version:
    warnings.warn(
        f"veros-extra-setups version ({this_version}) does not match Veros core version "
        f"({veros_version}). Consider running `pip install veros-extra-setups=={veros_version}`."
    )

del this_version, veros_version, _sanitize_version, warnings

__VEROS_INTERFACE__ = dict(
    name='extra-setups',
)
