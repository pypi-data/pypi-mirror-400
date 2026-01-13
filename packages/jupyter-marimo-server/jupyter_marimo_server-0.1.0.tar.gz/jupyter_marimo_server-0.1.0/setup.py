import setuptools

setuptools.setup(
    name="jupyter-marimo-server",
    packages=["jupyter_marimo_server"],
    entry_points={
        "jupyter_serverproxy_servers": [
            # name = packagename:function_name
            "marimo = jupyter_marimo_server:setup_marimo",
        ]
    },
    install_requires=["jupyter-server-proxy"],
    package_data={
        "jupyter_marimo_server": ["icons/*"],
    },
)
