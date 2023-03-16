if __name__ == "__main__":
    import subprocess
    import os
    import tray

    def run_scr():
        subprocess.run(
            ["python",
             os.path.join(
                 os.path.abspath(os.path.dirname(__file__)),
                 "screenshot"
             )
             ]
        )

    def run_opt():
        print("pon")

    tray.create_tray(run_scr, run_opt)
