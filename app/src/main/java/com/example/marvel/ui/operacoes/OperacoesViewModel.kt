package com.example.marvel.ui.operacoes

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.marvel.data.repository.PosterRepository
import com.example.marvel.model.FilmeModel
import com.example.marvel.util.OperacaoDateParser
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import java.time.LocalDate
import javax.inject.Inject

sealed class OperacoesUiState {
    data class Success(
        val filmes: List<FilmeModel>,
        val isVazio: Boolean,
        val isLoading: Boolean = false,
        val timestamp: Long = System.currentTimeMillis()
    ) : OperacoesUiState()
}

@HiltViewModel
class OperacoesViewModel @Inject constructor(
    private val posterRepository: PosterRepository?
) : ViewModel() {

    constructor() : this(null)

    private val _uiState = MutableStateFlow<OperacoesUiState>(OperacoesUiState.Success(emptyList(), false))
    val uiState: StateFlow<OperacoesUiState> = _uiState.asStateFlow()

    private var categoriaAtual: String = "TODOS"
    private var listaFuturaCompleta: List<FilmeModel> = emptyList()

    init {
        carregarOperacoes()
    }

    /**
     * Carrega e filtra todas as operações a partir da data atual do dispositivo (LocalDate.now()).
     * REGRA DE FILTRO NA CAMADA DE DADOS:
     * - Utiliza LocalDate.now() dinamicamente a cada carregamento.
     * - Mantém somente lançamentos futuros (data >= hoje).
     * - Ordena do mais próximo para o mais distante (ordem crescente).
     * - Itens sem data ("A definir") ficam no final com texto "DATA A DEFINIR".
     * - O primeiro item (mais próximo) recebe destaque com chip de contagem regressiva.
     */
    fun carregarOperacoes() {
        val hoje = LocalDate.now()
        val masterList = obterMasterListDeOperacoes()

        // Preserva URLs de pôsteres já resolvidos em memória para não resetar ao reabrir/onResume
        val posterCache = listaFuturaCompleta.associate { (it.tituloOriginal ?: it.titulo) to it.posterUrl }
        masterList.forEach { filme ->
            val key = filme.tituloOriginal ?: filme.titulo
            if (filme.posterUrl.isNullOrBlank() && !posterCache[key].isNullOrBlank()) {
                filme.posterUrl = posterCache[key]
            }
        }

        // 1. Processa e realiza o parse de data de cada operação
        val processados = masterList.map { filme ->
            val data = OperacaoDateParser.parseIsoOrLegacy(filme.dataIso, filme.mes, filme.ano)
            filme.dataParsed = data
            filme.dataFormatada = OperacaoDateParser.formatarExibicao(filme.dataIso, filme.mes, filme.ano, data)
            filme
        }

        // 2. Filtra: data >= hoje (lançamentos de hoje contam como futuro) OU "A definir" (data == null)
        val futuros = processados.filter { filme ->
            val data = filme.dataParsed
            data == null || !data.isBefore(hoje)
        }

        // 3. Ordena: ordem crescente por data, com itens sem data (null) no final
        val ordenados = futuros.sortedWith(
            compareBy(nullsLast()) { it.dataParsed }
        )

        // 4. Atribui destaque ao primeiro item da lista com contagem regressiva
        ordenados.forEachIndexed { index, filme ->
            if (index == 0) {
                filme.isDestaque = true
                filme.contadorRegressivo = OperacaoDateParser.calcularContagemRegressiva(hoje, filme.dataParsed)
            } else {
                filme.isDestaque = false
                filme.contadorRegressivo = null
            }
        }

        listaFuturaCompleta = ordenados
        aplicarFiltroCategoria(categoriaAtual)

        // 5. Carrega pôsteres via PosterRepository com fallbacks (Item -> TMDB -> Wikipedia -> Placeholder)
        posterRepository?.let { repo ->
            viewModelScope.launch {
                var mudou = false
                listaFuturaCompleta.forEach { filme ->
                    if (filme.posterUrl.isNullOrBlank()) {
                        val res = repo.obterPoster(filme)
                        if (!res.url.isNullOrBlank()) {
                            filme.posterUrl = res.url
                            mudou = true
                        }
                    }
                }
                if (mudou) {
                    aplicarFiltroCategoria(categoriaAtual)
                }
            }
        }
    }

    /**
     * Filtra por categoria ("TODOS", "CINEMA", "DISNEY+") sobre a lista já filtrada por data.
     */
    fun filtrarPorCategoria(categoria: String) {
        categoriaAtual = categoria
        aplicarFiltroCategoria(categoriaAtual)
    }

    private fun aplicarFiltroCategoria(categoria: String) {
        val filtrados = if (categoria.equals("TODOS", ignoreCase = true)) {
            listaFuturaCompleta
        } else {
            listaFuturaCompleta.filter { it.categoria.equals(categoria, ignoreCase = true) }
        }

        _uiState.value = OperacoesUiState.Success(
            filmes = ArrayList(filtrados),
            isVazio = filtrados.isEmpty(),
            timestamp = System.currentTimeMillis()
        )
    }

    private fun obterMasterListDeOperacoes(): List<FilmeModel> {
        return listOf(
            FilmeModel.criarLancamento(
                "2025-02-14",
                "CAPITÃO AMÉRICA: ADMIRÁVEL MUNDO NOVO",
                "Captain America: Brave New World",
                "FASE 5 // CINEMAS",
                "Sam Wilson enfrenta conspiração global de Adamantium e o Presidente Ross transformado em Hulk Vermelho.",
                "CINEMA",
                true,
                "[MISSÃO CONCLUÍDA]",
                "https://upload.wikimedia.org/wikipedia/en/6/6f/Captain_America_Brave_New_World_poster.jpg"
            ),
            FilmeModel.criarLancamento(
                "2025-03-04",
                "DEMOLIDOR: RENASCIDO (BORN AGAIN)",
                "Daredevil: Born Again",
                "FASE 5 // DISNEY+ SÉRIE",
                "Matt Murdock e Wilson Fisk em rota de colisão nas ruas de Nova York com a chegada do Justiceiro.",
                "DISNEY+",
                true,
                "[MISSÃO CONCLUÍDA]",
                "https://upload.wikimedia.org/wikipedia/en/c/cb/Daredevil_Born_Again_logo.jpg"
            ),
            FilmeModel.criarLancamento(
                "2025-05-02",
                "THUNDERBOLTS*",
                "Thunderbolts*",
                "FASE 5 // CINEMAS",
                "Yelena Belova, Soldado Invernal e anti-heróis renegados da Marvel em missão de alto risco contra o Sentinela.",
                "CINEMA",
                true,
                "[MISSÃO CONCLUÍDA]",
                "https://upload.wikimedia.org/wikipedia/en/5/53/Thunderbolts%2A_teaser_poster.jpg"
            ),
            FilmeModel.criarLancamento(
                "2025-07-25",
                "QUARTETO FANTÁSTICO: PRIMEIROS PASSOS",
                "The Fantastic Four: First Steps",
                "FASE 6 // CINEMAS",
                "A Primeira Família da Marvel (Pedro Pascal como Reed Richards) nos anos 60 contra Galactus e o Surfista Prateado.",
                "CINEMA",
                true,
                "[MISSÃO CONCLUÍDA]",
                "https://upload.wikimedia.org/wikipedia/en/0/08/The_Fantastic_Four_First_Steps_poster.jpg"
            ),
            FilmeModel.criarLancamento(
                "2026-07-24",
                "HOMEM-ARANHA 4",
                "Spider-Man 4",
                "FASE 6 // CINEMAS",
                "Peter Parker anônimo e solo atuando nas ruas de Nova York pós-feitiço do Doutor Estranho.",
                "CINEMA",
                true,
                "[MISSÃO CONCLUÍDA]",
                "https://upload.wikimedia.org/wikipedia/en/0/00/Spider-Man_No_Way_Home_poster.jpg"
            ),
            FilmeModel.criarLancamento(
                "2026-12-18",
                "VINGADORES: DOOMSDAY",
                "Avengers: Doomsday",
                "FASE 6 // CINEMAS GLOBAIS",
                "O retorno histórico dos irmãos Russo na direção e Robert Downey Jr. como Victor von Doom (Doutor Destino).",
                "CINEMA",
                false,
                "[EM PRODUÇÃO]",
                "https://upload.wikimedia.org/wikipedia/en/e/ee/Avengers_Doomsday_poster.jpg"
            ),
            FilmeModel.criarLancamento(
                "2027-12-17",
                "VINGADORES: GUERRAS SECRETAS",
                "Avengers: Secret Wars",
                "FASE 6 // CLÍMAX DA SAGA DO MULTIVERSO",
                "O colapso final de todas as realidades e a colisão no Battleworld unindo heróis de todas as eras.",
                "CINEMA",
                false,
                "[NÍVEL 8 // CLASSIFICADO]",
                "https://upload.wikimedia.org/wikipedia/en/0/08/Secretwars1.png"
            ),
            FilmeModel.criarLancamento(
                null,
                "BLADE",
                "Blade",
                "FASE 6 // CINEMAS",
                "Mahershala Ali estrela como Eric Brooks, o lendário caçador de vampiros meio-humano meio-vampiro no MCU.",
                "CINEMA",
                false,
                "[EM DESENVOLVIMENTO]",
                "https://upload.wikimedia.org/wikipedia/en/3/37/Blade_%28Marvel_Comics%29.png"
            ),
            FilmeModel.criarLancamento(
                null,
                "ARMOR WARS",
                "Armor Wars",
                "FASE 6 // CINEMAS",
                "James Rhodes (Máquina de Combate) precisa proteger a tecnologia de Tony Stark caída em mãos erradas.",
                "CINEMA",
                false,
                "[EM DESENVOLVIMENTO]",
                "https://upload.wikimedia.org/wikipedia/en/2/2d/Iron_Man_225.jpg"
            ),
            FilmeModel.criarLancamento(
                null,
                "CORAÇÃO DE FERRO (IRONHEART)",
                "Ironheart",
                "FASE 5 // DISNEY+ SÉRIE",
                "Riri Williams retorna a Chicago balanceando ciência e magia contra Parker Robbins (Capuz).",
                "DISNEY+",
                false,
                "[EM DESENVOLVIMENTO]",
                "https://thumb.wikimedia.org/wikipedia/en/thumb/e/e9/Ironheart_%28miniseries%29_logo.png/330px-Ironheart_%28miniseries%29_logo.png"
            )
        )
    }
}
