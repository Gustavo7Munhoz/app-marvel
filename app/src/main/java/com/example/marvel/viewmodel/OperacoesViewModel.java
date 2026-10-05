package com.example.marvel.viewmodel;

import androidx.lifecycle.LiveData;
import androidx.lifecycle.MutableLiveData;
import androidx.lifecycle.ViewModel;
import com.example.marvel.model.OperacaoModel;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Date;
import java.util.List;

/**
 * ViewModel em Java responsável pela lógica de dados e filtros do Painel de Operações.
 */
public class OperacoesViewModel extends ViewModel {

    public enum FiltroOperacao {
        TODOS,
        FUTUROS,
        CONCLUIDOS,
        CINEMA,
        DISNEY_PLUS
    }

    private final List<OperacaoModel> catalogoCompleto = new ArrayList<>();
    private final MutableLiveData<List<OperacaoModel>> operacoesFiltradas = new MutableLiveData<>();
    private FiltroOperacao filtroAtual = FiltroOperacao.FUTUROS;

    public OperacoesViewModel() {
        carregarCatalogoOperacoes();
        // Por padrão, inicializa com o filtro FUTUROS ativo
        aplicarFiltro(FiltroOperacao.FUTUROS);
    }

    public LiveData<List<OperacaoModel>> getOperacoesFiltradas() {
        return operacoesFiltradas;
    }

    public FiltroOperacao getFiltroAtual() {
        return filtroAtual;
    }

    /**
     * Aplica o filtro selecionado no ChipGroup.
     * Ao selecionar FUTUROS, oculta todas as operações com data anterior à data atual do sistema.
     */
    public void aplicarFiltro(FiltroOperacao filtro) {
        this.filtroAtual = filtro;
        Date dataAtual = new Date();
        List<OperacaoModel> resultado = new ArrayList<>();

        for (OperacaoModel op : catalogoCompleto) {
            switch (filtro) {
                case FUTUROS:
                    // Exibe apenas lançamentos cuja data é posterior à data atual do sistema
                    if (op.getDataLancamento() != null && op.getDataLancamento().after(dataAtual)) {
                        resultado.add(op);
                    }
                    break;

                case CONCLUIDOS:
                    // Exibe apenas operações cuja data já passou em relação à data atual do sistema
                    if (op.getDataLancamento() != null && op.getDataLancamento().before(dataAtual)) {
                        resultado.add(op);
                    }
                    break;

                case CINEMA:
                    if ("CINEMA".equalsIgnoreCase(op.getCategoria())) {
                        resultado.add(op);
                    }
                    break;

                case DISNEY_PLUS:
                    if ("DISNEY+".equalsIgnoreCase(op.getCategoria())) {
                        resultado.add(op);
                    }
                    break;

                case TODOS:
                default:
                    resultado.add(op);
                    break;
            }
        }

        operacoesFiltradas.setValue(resultado);
    }

    /**
     * Catálogo tático oficial com as operações do MCU (Passadas e Futuras).
     */
    private void carregarCatalogoOperacoes() {
        catalogoCompleto.clear();

        // 1. CAPITÃO AMÉRICA: ADMIRÁVEL MUNDO NOVO (Fevereiro de 2025 - Concluído)
        catalogoCompleto.add(new OperacaoModel(
                1,
                "CAPITÃO AMÉRICA: ADMIRÁVEL MUNDO NOVO",
                "FASE 5 // CINEMAS",
                "Sam Wilson assume o manto definitivo e enfrenta conspiração global de Adamantium e o Presidente Ross transformado em Hulk Vermelho.",
                "CINEMA",
                criarData(2025, Calendar.FEBRUARY, 14),
                "14 DE FEVEREIRO DE 2025",
                "[MISSÃO CONCLUÍDA]",
                false,
                null
        ));

        // 2. DEMOLIDOR: RENASCIDO (Março de 2025 - Concluído)
        catalogoCompleto.add(new OperacaoModel(
                2,
                "DEMOLIDOR: RENASCIDO (BORN AGAIN)",
                "FASE 5 // DISNEY+ SÉRIE",
                "Matt Murdock e Wilson Fisk em rota de colisão nas ruas de Hell's Kitchen com a intervenção do Justiceiro.",
                "DISNEY+",
                criarData(2025, Calendar.MARCH, 4),
                "04 DE MARÇO DE 2025",
                "[MISSÃO CONCLUÍDA]",
                false,
                null
        ));

        // 3. THUNDERBOLTS* (Maio de 2025 - Próximo Lançamento / Ameaça Iminente)
        catalogoCompleto.add(new OperacaoModel(
                3,
                "THUNDERBOLTS*",
                "FASE 5 // CINEMAS",
                "Yelena Belova, Soldado Invernal, Guardião Vermelho e operativos renegados em missão classificada contra o Sentinela.",
                "CINEMA",
                criarData(2025, Calendar.MAY, 2),
                "02 DE MAIO DE 2025",
                "[LANÇAMENTO IMINENTE]",
                true,
                "STATUS: T-MINUS 35 DIAS // PROTOCOLO ATIVO"
        ));

        // 4. QUARTETO FANTÁSTICO: PRIMEIROS PASSOS (Julho de 2025 - Futuro)
        catalogoCompleto.add(new OperacaoModel(
                4,
                "QUARTETO FANTÁSTICO: PRIMEIROS PASSOS",
                "FASE 6 // CINEMAS",
                "A Primeira Família da Marvel (Pedro Pascal como Reed Richards) em Nova York retrofuturista dos anos 60 contra Galactus.",
                "CINEMA",
                criarData(2025, Calendar.JULY, 25),
                "25 DE JULHO DE 2025",
                "[EM PÓS-PRODUÇÃO]",
                false,
                null
        ));

        // 5. VINGADORES: DOOMSDAY (Maio de 2026 - Futuro)
        catalogoCompleto.add(new OperacaoModel(
                5,
                "VINGADORES: DOOMSDAY",
                "FASE 6 // CINEMAS GLOBAIS",
                "Os irmãos Russo retornam à direção com Robert Downey Jr. personificando Victor von Doom em escala de ameaça global.",
                "CINEMA",
                criarData(2026, Calendar.MAY, 1),
                "01 DE MAIO DE 2026",
                "[EM PRODUÇÃO]",
                false,
                null
        ));

        // 6. HOMEM-ARANHA 4 (Julho de 2026 - Futuro)
        catalogoCompleto.add(new OperacaoModel(
                6,
                "HOMEM-ARANHA 4",
                "FASE 6 // CINEMAS",
                "Peter Parker atuando de forma clandestina nas ruas de Nova York pós-feitiço esquecimento de Stephen Strange.",
                "CINEMA",
                criarData(2026, Calendar.JULY, 10),
                "10 DE JULHO DE 2026",
                "[ARQUIVO // FUTURO]",
                false,
                null
        ));

        // 7. VINGADORES: GUERRAS SECRETAS (Maio de 2027 - Futuro Clímax)
        catalogoCompleto.add(new OperacaoModel(
                7,
                "VINGADORES: GUERRAS SECRETAS (SECRET WARS)",
                "FASE 6 // CLÍMAX DA SAGA",
                "O colapso inevitável de todas as realidades alternativas e a fusão de universos no Battleworld.",
                "CINEMA",
                criarData(2027, Calendar.MAY, 7),
                "07 DE MAIO DE 2027",
                "[NÍVEL 8 // CLASSIFICADO]",
                false,
                null
        ));
    }

    private Date criarData(int ano, int mesCalendar, int dia) {
        Calendar cal = Calendar.getInstance();
        cal.set(ano, mesCalendar, dia, 0, 0, 0);
        return cal.getTime();
    }
}
