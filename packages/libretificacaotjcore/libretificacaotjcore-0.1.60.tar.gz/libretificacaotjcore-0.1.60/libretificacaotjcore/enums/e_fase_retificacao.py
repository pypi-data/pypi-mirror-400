from enum import Enum


class EFaseRetificacao(Enum):
    NaoIniciado = 0
    SolicitacaoXml = 1
    AguardandoXml = 2
    DownloadXml = 3
    ExtraindoDadosDoXml = 4
    #? Abertura de Competencia
    EstruturandoXmlAberturaCompetencia = 5
    AberturaDeCompetencia = 6
    ConsultandoESocialAberturaCompetencia = 7
    #? Rubricas
    EstruturandoXmlInclusaoRubricas = 8
    InclusaoDasRubricas = 9
    ConsultandoESocialInclusaoRubricas = 10
    #? Exclusao de Pagamentos
    EstruturandoXmlExclusaoPagamentos = 11
    ExclusaoDePagamentos = 12
    ConsultandoESocialExclusaoPagamentos = 13
    #? Retificacao
    EstruturandoXmlRetificacaoRemuneracao = 14
    RetificacaoDaRemuneracao = 15
    ConsultandoESocialRetificacaoRemuneracao = 16
    #? Desligamento
    EstruturandoXmlDesligamento = 17
    Desligamento = 18
    ConsultandoESocialDesligamento = 19
    #? Inclusao de Pagamentos
    EstruturandoXmlInclusaoPagamentos = 20
    InclusaoDosPagamentos = 21
    ConsultandoESocialInclusaoPagamentos = 22
    #? Fechamento de Competencia
    EstruturandoXmlFechamentoCompetencia = 23
    FechamentoDeCompetencia = 24
    ConsultandoESocialFechamentoCompetencia = 25
    Finalizado = 26
