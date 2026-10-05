package com.example.marvel.model;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

/**
 * Modelo de dados para Operações S.H.I.E.L.D. (Lançamentos MCU)
 * Suporta cálculo de datas para filtros de lançamentos futuros e concluídos.
 */
public class OperacaoModel {
    private int id;
    private String titulo;
    private String faseStatus;
    private String sinopse;
    private String categoria; // "CINEMA" ou "DISNEY+"
    private Date dataLancamento;
    private String dataFormatada;
    private String statusCarimbo; // ex: "[MISSÃO CONCLUÍDA]", "[LANÇAMENTO IMINENTE]"
    private boolean destaque; // true para forçar card Hero
    private String contadorRegressivo; // ex: "STATUS: T-MINUS 35 DIAS // PROTOCOLO ATIVO"

    public OperacaoModel() {
    }

    public OperacaoModel(int id, String titulo, String faseStatus, String sinopse, String categoria, Date dataLancamento, String dataFormatada, String statusCarimbo, boolean destaque, String contadorRegressivo) {
        this.id = id;
        this.titulo = titulo;
        this.faseStatus = faseStatus;
        this.sinopse = sinopse;
        this.categoria = categoria;
        this.dataLancamento = dataLancamento;
        this.dataFormatada = dataFormatada;
        this.statusCarimbo = statusCarimbo;
        this.destaque = destaque;
        this.contadorRegressivo = contadorRegressivo;
    }

    public int getId() {
        return id;
    }

    public void setId(int id) {
        this.id = id;
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

    public Date getDataLancamento() {
        return dataLancamento;
    }

    public void setDataLancamento(Date dataLancamento) {
        this.dataLancamento = dataLancamento;
    }

    public String getDataFormatada() {
        if (dataFormatada != null && !dataFormatada.isEmpty()) {
            return dataFormatada;
        }
        if (dataLancamento != null) {
            SimpleDateFormat sdf = new SimpleDateFormat("MMMM yyyy", new Locale("pt", "BR"));
            return sdf.format(dataLancamento).toUpperCase();
        }
        return "DATA NÃO CONFIRMADA";
    }

    public void setDataFormatada(String dataFormatada) {
        this.dataFormatada = dataFormatada;
    }

    public String getStatusCarimbo() {
        if (statusCarimbo != null && !statusCarimbo.isEmpty()) {
            return statusCarimbo;
        }
        return isFuturo() ? "[ARQUIVO // FUTURO]" : "[MISSÃO CONCLUÍDA]";
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

    /**
     * Verifica se a operação é um lançamento futuro em relação à data atual do sistema.
     */
    public boolean isFuturo() {
        if (dataLancamento == null) return true;
        return dataLancamento.after(new Date());
    }
}
