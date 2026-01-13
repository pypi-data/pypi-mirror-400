import json
from nfe.HntException import HntException
from nfe.nfe_caixa import NFeCaixa
class TestNFeCaixa:
    def setup_method(self, method):
        with open(f"./devdata/json/{method.__name__}.json", "r", encoding="utf-8") as arquivo_json: nfe = json.load(arquivo_json)
        self.nfe = nfe
        self.nfe_caixa = None

    def test_cfp_15861804877(self):
        self.nfe_caixa = NFeCaixa().build('GHN-69904', self.nfe)

    def test_many_fornecedores_cfp_15861804877(self):
        try:
            self.nfe_caixa = NFeCaixa().build('GHN-69904', self.nfe)
            assert False, "Expected HntException was not raised"
        except HntException as e:
            assert str(e) == "HNTException: multiple fornecedores_caixa found and form.sap_cod_fornecedor None did not match any"

    def test_not_found_material_cfp_15861804877(self):
        try:
            self.nfe_caixa = NFeCaixa().build('GHN-69904', self.nfe)
            assert False, "Expected HntException was not raised"
        except HntException as e:
            assert str(e) == "HNTException: Could not find FornecedorMaterial, nro_documento: 15861804877, cod_material_fornecedor: 559133"


    def teardown_method(self, method):
        if self.nfe_caixa is not None:
            with open(f"./output/json/{method.__name__}.json", "w", encoding="utf-8") as json_file:
                json.dump(self.nfe_caixa.model_dump(mode="json"), json_file, ensure_ascii=False, indent=4, default=str)

