package com.example.marvel.model;

/**
 * Modelo de dados para operações de lançamentos (MCU / S.H.I.E.L.D. Calendário)
 */
public class FilmeModel {
    private String dataIso; // "yyyy-MM-dd" ou null
    private String tituloOriginal; // Ex: "Avengers: Doomsday"
    private String posterUrl;
    private String mes;
    private String ano;
    private String titulo;
    private String faseStatus;
    private String sinopse;
    private String categoria; // "CINEMA" ou "DISNEY+"
    private boolean concluido; // true se já lançado, false se futuro
    private String statusCarimbo; // ex: "[MISSÃO CONCLUÍDA]", "[EM ANDAMENTO]", "[ARQUIVO]"
    private boolean destaque; // true se for o card Hero de Ameaça Iminente
    private String contadorRegressivo; // ex: "EM 74 DIAS"
    private java.time.LocalDate dataParsed;
    private String dataFormatada;

    public FilmeModel() {
    }

    public FilmeModel(String mes, String ano, String titulo, String faseStatus, String sinopse, String categoria, boolean concluido) {
        this(null, mes, ano, titulo, null, faseStatus, sinopse, categoria, concluido, concluido ? "[MISSÃO CONCLUÍDA]" : "[EM ANDAMENTO]", false, null);
    }

    public FilmeModel(String mes, String ano, String titulo, String faseStatus, String sinopse, String categoria, boolean concluido, String statusCarimbo) {
        this(null, mes, ano, titulo, null, faseStatus, sinopse, categoria, concluido, statusCarimbo, false, null);
    }

    public FilmeModel(String mes, String ano, String titulo, String faseStatus, String sinopse, String categoria, boolean concluido, String statusCarimbo, boolean destaque, String contadorRegressivo) {
        this(null, mes, ano, titulo, null, faseStatus, sinopse, categoria, concluido, statusCarimbo, destaque, contadorRegressivo);
    }

    public static FilmeModel criarLancamento(String dataIso, String titulo, String tituloOriginal, String faseStatus, String sinopse, String categoria, boolean concluido, String statusCarimbo) {
        return criarLancamento(dataIso, titulo, tituloOriginal, faseStatus, sinopse, categoria, concluido, statusCarimbo, null);
    }

    public static FilmeModel criarLancamento(String dataIso, String titulo, String tituloOriginal, String faseStatus, String sinopse, String categoria, boolean concluido, String statusCarimbo, String posterUrl) {
        FilmeModel model = new FilmeModel(dataIso, null, null, titulo, tituloOriginal, faseStatus, sinopse, categoria, concluido, statusCarimbo, false, null);
        model.setPosterUrl(posterUrl);
        return model;
    }

    public FilmeModel(String dataIso, String mes, String ano, String titulo, String tituloOriginal, String faseStatus, String sinopse, String categoria, boolean concluido, String statusCarimbo, boolean destaque, String contadorRegressivo) {
        this.dataIso = dataIso;
        this.titulo = titulo;
        this.tituloOriginal = tituloOriginal != null ? tituloOriginal : titulo;
        this.faseStatus = faseStatus;
        this.sinopse = sinopse;
        this.categoria = categoria;
        this.concluido = concluido;
        this.statusCarimbo = statusCarimbo;
        this.destaque = destaque;
        this.contadorRegressivo = contadorRegressivo;

        if (dataIso != null && !dataIso.trim().isEmpty() && !dataIso.toUpperCase(java.util.Locale.ROOT).contains("DEFINIR")) {
            try {
                this.dataParsed = java.time.LocalDate.parse(dataIso.trim(), java.time.format.DateTimeFormatter.ISO_LOCAL_DATE);
                this.ano = String.valueOf(this.dataParsed.getYear());
                this.mes = String.format(java.util.Locale.getDefault(), "%02d", this.dataParsed.getMonthValue());
                this.dataFormatada = String.format(java.util.Locale.getDefault(), "%02d/%02d/%04d", this.dataParsed.getDayOfMonth(), this.dataParsed.getMonthValue(), this.dataParsed.getYear());
            } catch (Exception e) {
                this.dataParsed = null;
                this.ano = ano != null ? ano : "A definir";
                this.mes = mes != null ? mes : "A definir";
                this.dataFormatada = "DATA A DEFINIR";
            }
        } else {
            this.ano = ano != null ? ano : "A definir";
            this.mes = mes != null ? mes : "A definir";
            this.dataFormatada = "DATA A DEFINIR";
        }
    }

    public String getMes() {
        return mes;
    }

    public void setMes(String mes) {
        this.mes = mes;
    }

    public String getAno() {
        return ano;
    }

    public void setAno(String ano) {
        this.ano = ano;
    }

    public String getTitulo() {
        return titulo;
    }

    public void setTitulo(String titulo) {
        this.titulo = titulo;
    }

    public String getFaseStatus() {
        return faseStatus;
    }

    public void setFaseStatus(String faseStatus) {
        this.faseStatus = faseStatus;
    }

    public String getSinopse() {
        return sinopse;
    }

    public void setSinopse(String sinopse) {
        this.sinopse = sinopse;
    }

    public String getCategoria() {
        return categoria;
    }

    public void setCategoria(String categoria) {
        this.categoria = categoria;
    }

    public boolean isConcluido() {
        return concluido;
    }

    public void setConcluido(boolean concluido) {
        this.concluido = concluido;
    }

    public String getStatusCarimbo() {
        if (statusCarimbo != null && !statusCarimbo.isEmpty()) {
            return statusCarimbo;
        }
        return concluido ? "[MISSÃO CONCLUÍDA]" : "[ARQUIVO // FUTURO]";
    }

    public void setStatusCarimbo(String statusCarimbo) {
        this.statusCarimbo = statusCarimbo;
    }

    public boolean isDestaque() {
        return destaque;
    }

    public void setDestaque(boolean destaque) {
        this.destaque = destaque;
    }

    public String getContadorRegressivo() {
        return contadorRegressivo;
    }

    public void setContadorRegressivo(String contadorRegressivo) {
        this.contadorRegressivo = contadorRegressivo;
    }

    public java.time.LocalDate getDataParsed() {
        return dataParsed;
    }

    public void setDataParsed(java.time.LocalDate dataParsed) {
        this.dataParsed = dataParsed;
    }

    public String getDataFormatada() {
        return dataFormatada;
    }

    public void setDataFormatada(String dataFormatada) {
        this.dataFormatada = dataFormatada;
    }

    public String getDataIso() {
        return dataIso;
    }

    public void setDataIso(String dataIso) {
        this.dataIso = dataIso;
    }

    public String getTituloOriginal() {
        return tituloOriginal != null ? tituloOriginal : titulo;
    }

    public void setTituloOriginal(String tituloOriginal) {
        this.tituloOriginal = tituloOriginal;
    }

    public String getPosterUrl() {
        return posterUrl;
    }

    public void setPosterUrl(String posterUrl) {
        this.posterUrl = posterUrl;
    }
}
