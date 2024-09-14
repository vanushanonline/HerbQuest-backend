import pytest

def run_tests():
    # List of test files to run
    test_files = [
        "test_login.py",
        "test_process.py",
        "test_regsiter.py",
        ]

    # Run pytest for the specified test files
    pytest.main(test_files + ["-p", "no:warnings","-v","--html=report.html","--self-contained-html"])

if __name__ == "__main__":
    run_tests()