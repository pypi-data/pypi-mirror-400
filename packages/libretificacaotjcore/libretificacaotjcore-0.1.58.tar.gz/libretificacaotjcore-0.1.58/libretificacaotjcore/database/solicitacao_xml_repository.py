import uuid

class SolicitacaoXmlsRepository:
    def __init__(self, db):
        self.__db = db

    async def inserir_solicitacao_xml(self, solicitacao_xml: dict) -> bool:
        
        try:
            solicitacao_xml_no_db = await self.__db.solicitacao_xmls.find_one(
                {"solicitacaoId": solicitacao_xml["solicitacaoId"]}
            )

            if solicitacao_xml_no_db is None:
                await self.__db.solicitacao_xmls.insert_one(solicitacao_xml)
                return True

            await self.__db.solicitacao_xmls.delete_one(
                   {"solicitacaoId": solicitacao_xml["solicitacaoId"]}
            )
            await self.__db.solicitacao_xmls.insert_one(solicitacao_xml)
            return True
        except Exception as e:
            print(f"❌ Erro ao inserir o solicitacao xml: {e}")
            return False
        
    async def buscar_por_solicitacao_id(self, solicitacaoId: int) -> dict:
        try:
            return await self.__db.solicitacao_xmls.find_one({"solicitacaoId": solicitacaoId})
        except Exception as e:
            print(f"❌ Erro ao buscar solicitacao xml por solicitacaoId: {e}")
            return {}
        
    async def remover_por_solicitacao_id(self, solicitacaoId: int) -> bool:
        try:
            await self.__db.solicitacao_xmls.delete_one({"solicitacaoId": solicitacaoId})
            return True
        except Exception as e:
            print(f"❌ Erro ao remover solicitacao xml por solicitacaoId: {e}")
            return False