import unittest

class BasicImportTest(unittest.TestCase):
    def test_package_import(self):
        try:
            import sir3stoolkit  
        except ImportError as e:
            self.fail(f"Import failed: {e}")
        try:
            SIR3S_SIRGRAF_DIR = r"C:\3S\SIR 3S\SirGraf-90-15-00-20x64_Quebec-Upd1" #change to local path
            
            from sir3stoolkit.core import wrapper
            wrapper.Initialize_Toolkit(SIR3S_SIRGRAF_DIR)
            s3s = wrapper.SIR3S_Model()
            s3s = wrapper.SIR3S_View()

            from sir3stoolkit.mantle.dataframes import SIR3S_Model_Dataframes
            s3s = SIR3S_Model_Dataframes()

            from sir3stoolkit.mantle.alternative_models import SIR3S_Model_Alternative_Models
            s3s = SIR3S_Model_Alternative_Models()

            from sir3stoolkit.mantle.plotting import SIR3S_Model_Plotting
            s3s = SIR3S_Model_Plotting

            from sir3stoolkit.mantle.mantle import SIR3S_Model_Mantle
            s3s = SIR3S_Model_Mantle()

        except Exception as e:
            self.fail(f"Init or Import failed: {e}")

if __name__ == "__main__":
    unittest.main()