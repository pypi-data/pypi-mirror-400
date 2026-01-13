# *************************************************************************
#
#  Copyright (c) 2025 - Datatailr Inc.
#  All Rights Reserved.
#
#  This file is part of Datatailr and subject to the terms and conditions
#  defined in 'LICENSE.txt'. Unauthorized copying and/or distribution
#  of this file, in parts or full, via any medium is strictly prohibited.
# *************************************************************************
from datatailr import set_allow_unsafe_scheduling
from datatailr.logging import CYAN

set_allow_unsafe_scheduling(True)


def simple_workflow():
    from datatailr import workflow
    from data_pipelines.data_processing import func_no_args

    @workflow(name="Simple Data Pipeline - <>USERNAME<>")
    def simple_data_pipeline():
        func_no_args()

    return simple_data_pipeline


def simple_app():
    from datatailr import App
    from dashboards.app import main

    app = App(
        name="Simple Dashboard App - <>USERNAME<>",
        entrypoint=main,
        python_requirements="streamlit",
    )
    return app


def simple_service():
    from datatailr import Service
    from services.flask_service import main

    service = Service(
        name="Simple Service - <>USERNAME<>",
        entrypoint=main,
        python_requirements="flask",
    )
    return service


def simple_excel_addin():
    from datatailr import ExcelAddin, Resources
    from excel_addins.addin import main as addin_main

    addin = ExcelAddin(
        name="Simple Excel Addin - <>USERNAME<>",
        entrypoint=addin_main,
        resources=Resources(memory="4g", cpu=1),
        python_version="3.10",
        python_requirements=["numpy", "pandas"],
    )
    return addin


def deploy_pipeline():
    wf = simple_workflow()
    print(CYAN("Deploying workflow..."))
    wf()


def deploy_app():
    app = simple_app()
    print(CYAN("Deploying app..."))
    app.run()


def deploy_service():
    service = simple_service()
    print(CYAN("Deploying service..."))
    service.run()


def deploy_excel_addin():
    addin = simple_excel_addin()
    print(CYAN("Deploying excel add-in..."))
    addin.run()


def deploy_all():
    deploy_pipeline()
    deploy_app()
    deploy_service()
    deploy_excel_addin()


def main():
    import sys

    if len(sys.argv) < 2:
        print("Usage: python examples.py [all|data_pipeline|app|service|excel]")
        sys.exit(1)

    command = sys.argv[1]
    commands = {
        "all": deploy_all,
        "data_pipeline": deploy_pipeline,
        "app": deploy_app,
        "service": deploy_service,
        "excel": deploy_excel_addin,
    }

    if command in commands:
        commands[command]()
    else:
        print("Usage: python examples.py [all|data_pipeline|app|service|excel]")
        sys.exit(1)


if __name__ == "__main__":
    main()
