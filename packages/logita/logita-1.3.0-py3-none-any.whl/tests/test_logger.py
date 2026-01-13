import unittest
from logita.logger import Logita
import sys
import io

class TestLogita(unittest.TestCase):
    def setUp(self):
        """
        Runs before each test. Initializes a Logita instance.
        """
        self.logger = Logita(use_colors=False)  # Desactivamos colores para pruebas

        # Capturamos la salida de stdout para verificar los prints
        self.captured_output = io.StringIO()
        self._stdout = sys.stdout
        sys.stdout = self.captured_output

    def tearDown(self):
        """
        Runs after each test. Restores stdout.
        """
        sys.stdout = self._stdout

    def get_output(self):
        """
        Helper method to get printed output.
        """
        return self.captured_output.getvalue()

    def test_debug(self):
        self.logger.debug("Debug message")
        output = self.get_output()
        self.assertIn("Debug message", output)

    def test_info(self):
        self.logger.info("Info message")
        output = self.get_output()
        self.assertIn("Info message", output)

    def test_success(self):
        self.logger.success("Success message")
        output = self.get_output()
        self.assertIn("Success message", output)

    def test_warning(self):
        self.logger.warning("Warning message")
        output = self.get_output()
        self.assertIn("Warning message", output)

    def test_error(self):
        self.logger.error("Error message")
        output = self.get_output()
        self.assertIn("Error message", output)

    def test_critical(self):
        self.logger.critical("Critical message")
        output = self.get_output()
        self.assertIn("Critical message", output)

    def test_exception_logging(self):
        try:
            1 / 0
        except ZeroDivisionError:
            self.logger.exception("Caught an exception")

        output = self.get_output()
        self.assertIn("Caught an exception", output)
        self.assertIn("ZeroDivisionError", output)

    def test_context_manager_no_exception(self):
        with Logita(use_colors=False) as log:
            log.info("Inside context")
        output = self.get_output()
        self.assertIn("Inside context", output)

    def test_context_manager_with_exception(self):
        try:
            with Logita(use_colors=False) as log:
                raise ValueError("Test exception")
        except ValueError:
            pass  # Ignoramos la excepción para verificar el log
        output = self.get_output()
        self.assertIn("Exception captured in context: Test exception", output)
        self.assertIn("ValueError", output)

if __name__ == "__main__":
    unittest.main()
