package com.example.marvel.game;

import android.widget.TextView;
import com.example.marvel.R;

/**
 * Gerenciador tático do mini-game Termo Operativo (estilo Wordle da S.H.I.E.L.D.)
 */
public class TermoGameManager {

    public enum LetraStatus {
        CORRETA,
        POSICAO_ERRADA,
        AUSENTE
    }

    private String palavraCerta = "THORS"; // Palavra do Dia (5 letras)
    private int tentativaAtual = 0;
    private final int maxTentativas = 6;
    private boolean jogoFinalizado = false;

    public TermoGameManager() {
    }

    public TermoGameManager(String palavraCerta) {
        if (palavraCerta != null && palavraCerta.length() == 5) {
            this.palavraCerta = palavraCerta.toUpperCase();
        }
    }

    public void reiniciarJogo(String novaPalavra) {
        if (novaPalavra != null && novaPalavra.length() == 5) {
            this.palavraCerta = novaPalavra.toUpperCase();
        }
        this.tentativaAtual = 0;
        this.jogoFinalizado = false;
    }

    /**
     * Valida o palpite de 5 letras e aplica o estilo nas caixas de texto.
     */
    public boolean validarTentativa(String palpite, TextView[] caixas) {
        if (palpite == null || palpite.length() != 5 || caixas == null || caixas.length != 5) {
            return false;
        }
        if (jogoFinalizado) {
            return false;
        }

        palpite = palpite.toUpperCase();
        boolean[] palavraMatched = new boolean[5];
        LetraStatus[] status = new LetraStatus[5];

        // 1ª Passada: Letras na posição exata (VERDE)
        for (int i = 0; i < 5; i++) {
            char p = palpite.charAt(i);
            if (p == palavraCerta.charAt(i)) {
                status[i] = LetraStatus.CORRETA;
                palavraMatched[i] = true;
            }
        }

        // 2ª Passada: Letras presentes na palavra, mas em posição diferente (AMARELO/LARANJA)
        for (int i = 0; i < 5; i++) {
            if (status[i] != null) continue;
            char p = palpite.charAt(i);
            boolean encontrou = false;
            for (int j = 0; j < 5; j++) {
                if (!palavraMatched[j] && palavraCerta.charAt(j) == p) {
                    palavraMatched[j] = true;
                    encontrou = true;
                    break;
                }
            }
            status[i] = encontrou ? LetraStatus.POSICAO_ERRADA : LetraStatus.AUSENTE;
        }

        // Atualiza a interface gráfica das células
        boolean todosCorretos = true;
        for (int i = 0; i < 5; i++) {
            caixas[i].setText(String.valueOf(palpite.charAt(i)));
            switch (status[i]) {
                case CORRETA:
                    caixas[i].setBackgroundResource(R.drawable.bg_termo_correct);
                    break;
                case POSICAO_ERRADA:
                    caixas[i].setBackgroundResource(R.drawable.bg_termo_present);
                    todosCorretos = false;
                    break;
                case AUSENTE:
                    caixas[i].setBackgroundResource(R.drawable.bg_termo_absent);
                    todosCorretos = false;
                    break;
            }
        }

        tentativaAtual++;
        if (todosCorretos || tentativaAtual >= maxTentativas) {
            jogoFinalizado = true;
        }

        return todosCorretos;
    }

    public int getTentativaAtual() {
        return tentativaAtual;
    }

    public int getMaxTentativas() {
        return maxTentativas;
    }

    public boolean isJogoFinalizado() {
        return jogoFinalizado;
    }

    public String getPalavraCerta() {
        return palavraCerta;
    }
}
