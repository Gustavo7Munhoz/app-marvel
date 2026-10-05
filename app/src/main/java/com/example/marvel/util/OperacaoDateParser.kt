package com.example.marvel.util

import java.time.LocalDate
import java.time.YearMonth
import java.time.format.DateTimeFormatter
import java.time.temporal.ChronoUnit
import java.util.Locale

/**
 * Utilitário centralizado para leitura, interpretação (parse) e cálculo de datas
 * das operações de lançamentos do MCU / S.H.I.E.L.D. utilizando java.time.
 */
object OperacaoDateParser {

    private val MESES_MAP = mapOf(
        "JAN" to 1, "JANEIRO" to 1,
        "FEV" to 2, "FEVEREIRO" to 2,
        "MAR" to 3, "MARÇO" to 3, "MARCO" to 3,
        "ABR" to 4, "ABRIL" to 4,
        "MAI" to 5, "MAIO" to 5,
        "JUN" to 6, "JUNHO" to 6,
        "JUL" to 7, "JULHO" to 7,
        "AGO" to 8, "AGOSTO" to 8,
        "SET" to 9, "SETEMBRO" to 9,
        "OUT" to 10, "OUTUBRO" to 10,
        "NOV" to 11, "NOVEMBRO" to 11,
        "DEZ" to 12, "DEZEMBRO" to 12
    )

    /**
     * Realiza o parse prioritariamente a partir do campo dataIso (yyyy-MM-dd).
     * Caso não esteja preenchido ou falhe, recorre ao parse legado de mês e ano.
     */
    fun parseIsoOrLegacy(dataIso: String?, mesStr: String?, anoStr: String?): LocalDate? {
        if (!dataIso.isNullOrBlank() && !dataIso.contains("DEFINIR", ignoreCase = true)) {
            try {
                return LocalDate.parse(dataIso.trim(), DateTimeFormatter.ISO_LOCAL_DATE)
            } catch (_: Exception) {
            }
        }
        return parse(mesStr, anoStr)
    }

    /**
     * Realiza o parse da data a partir dos campos de mês e ano (ou strings compostas).
     * Se contiver apenas mês e ano, calcula o ÚLTIMO dia do respectivo mês para que
     * lançamentos que ainda possam acontecer no mês atual não sejam descartados.
     * Retorna null caso a data seja "A definir", inválida ou não consiga ser lida.
     */
    fun parse(mesStr: String?, anoStr: String?): LocalDate? {
        if (mesStr.isNullOrBlank() || anoStr.isNullOrBlank()) {
            return null
        }

        val mesLimpo = mesStr.trim().uppercase(Locale.getDefault())
        val anoLimpo = anoStr.trim()

        if (mesLimpo.contains("DEFINIR") || anoLimpo.contains("DEFINIR")) {
            return null
        }

        return try {
            val ano = anoLimpo.toIntOrNull() ?: return null
            val mesNum = MESES_MAP[mesLimpo] ?: mesLimpo.toIntOrNull() ?: return null

            if (mesNum !in 1..12) return null

            // Considera o ÚLTIMO dia do mês para datas mês/ano
            val yearMonth = YearMonth.of(ano, mesNum)
            yearMonth.atEndOfMonth()
        } catch (e: Exception) {
            null
        }
    }

    /**
     * Tenta realizar o parse a partir de um texto composto único (ex: "02/05/2025", "MAI/2026", "2026-05-02").
     */
    fun parseTexto(texto: String?): LocalDate? {
        if (texto.isNullOrBlank()) return null
        val limpo = texto.trim().uppercase(Locale.getDefault())

        if (limpo.contains("DEFINIR")) return null

        return try {
            // Tenta formato "MAI/2026" ou "MAI 2026"
            if (limpo.contains("/") || limpo.contains(" ")) {
                val partes = limpo.split(Regex("[/ ]+")).filter { it.isNotBlank() }
                if (partes.size == 2) {
                    val p1 = partes[0]
                    val p2 = partes[1]
                    if (p1.toIntOrNull() != null && p2.toIntOrNull() != null) {
                        val mes = p1.toInt()
                        val ano = p2.toInt()
                        if (mes in 1..12) return YearMonth.of(ano, mes).atEndOfMonth()
                    } else if (MESES_MAP.containsKey(p1) && p2.toIntOrNull() != null) {
                        return parse(p1, p2)
                    }
                } else if (partes.size == 3) {
                    // Dia/Mês/Ano
                    val dia = partes[0].toIntOrNull()
                    val mes = MESES_MAP[partes[1]] ?: partes[1].toIntOrNull()
                    val ano = partes[2].toIntOrNull()
                    if (dia != null && mes != null && ano != null && mes in 1..12) {
                        val maxDay = YearMonth.of(ano, mes).lengthOfMonth()
                        val diaValido = dia.coerceIn(1, maxDay)
                        return LocalDate.of(ano, mes, diaValido)
                    }
                }
            }
            // Tenta ISO (yyyy-MM-dd)
            LocalDate.parse(limpo, DateTimeFormatter.ISO_LOCAL_DATE)
        } catch (e: Exception) {
            null
        }
    }

    /**
     * Calcula o texto da contagem regressiva em relação à data atual (hoje).
     * Retorna "HOJE", "AMANHÃ" ou "EM X DIAS".
     */
    fun calcularContagemRegressiva(hoje: LocalDate, dataLancamento: LocalDate?): String {
        if (dataLancamento == null) {
            return "DATA A DEFINIR"
        }

        val dias = ChronoUnit.DAYS.between(hoje, dataLancamento)
        return when {
            dias <= 0L -> "HOJE"
            dias == 1L -> "AMANHÃ"
            else -> "EM $dias DIAS"
        }
    }

    /**
     * Formata a exibição amigável da data.
     * Datas completas: "dd/MM/yyyy" (ex: "18/12/2026").
     * Mês/ano legado: "DEZ / 2026".
     * Itens sem data retornam "DATA A DEFINIR".
     */
    fun formatarExibicao(dataIso: String?, mes: String?, ano: String?, data: LocalDate?): String {
        if (data == null) {
            return "DATA A DEFINIR"
        }
        if (!dataIso.isNullOrBlank() && !dataIso.contains("DEFINIR", ignoreCase = true)) {
            return String.format(Locale.getDefault(), "%02d/%02d/%04d", data.dayOfMonth, data.monthValue, data.year)
        }
        val mesNome = mes?.trim()?.uppercase(Locale.getDefault()) ?: ""
        val anoStr = ano?.trim() ?: data.year.toString()

        return if (mesNome.isNotEmpty() && !mesNome.contains("DEFINIR")) {
            "$mesNome / $anoStr"
        } else {
            String.format(Locale.getDefault(), "%02d/%02d/%04d", data.dayOfMonth, data.monthValue, data.year)
        }
    }

    fun formatarExibicao(mes: String?, ano: String?, data: LocalDate?): String {
        return formatarExibicao(null, mes, ano, data)
    }

    fun formatarExibicao(data: LocalDate?): String {
        if (data == null) return "DATA A DEFINIR"
        return String.format(Locale.getDefault(), "%02d/%02d/%04d", data.dayOfMonth, data.monthValue, data.year)
    }
}
