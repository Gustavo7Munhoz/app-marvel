package com.example.marvel.adapter;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.TextView;
import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;
import com.example.marvel.R;
import com.example.marvel.model.OperacaoModel;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;

/**
 * Adapter do RecyclerView para o Painel de Operações da S.H.I.E.L.D.
 * Suporta múltiplos ViewTypes:
 * - TYPE_DESTAQUE: Card 'Hero' para o lançamento futuro mais próximo (Ameaça Iminente).
 * - TYPE_TIMELINE: Nós da linha do tempo vertical para todos os outros itens.
 */
public class OperacoesAdapter extends RecyclerView.Adapter<RecyclerView.ViewHolder> {

    public static final int TYPE_DESTAQUE = 0;
    public static final int TYPE_TIMELINE = 1;

    private List<OperacaoModel> listaOperacoes;

    public OperacoesAdapter() {
        this.listaOperacoes = new ArrayList<>();
    }

    public OperacoesAdapter(List<OperacaoModel> listaOperacoes) {
        this.listaOperacoes = listaOperacoes != null ? listaOperacoes : new ArrayList<>();
    }

    public void setLista(List<OperacaoModel> novaLista) {
        this.listaOperacoes = novaLista != null ? novaLista : new ArrayList<>();
        notifyDataSetChanged();
    }

    public List<OperacaoModel> getLista() {
        return listaOperacoes;
    }

    /**
     * Identifica o ViewType de cada item:
     * O lançamento futuro mais próximo (ou item com flag destaque ativa) recebe TYPE_DESTAQUE.
     * Todos os outros recebem TYPE_TIMELINE.
     */
    @Override
    public int getItemViewType(int position) {
        if (listaOperacoes == null || listaOperacoes.isEmpty()) {
            return TYPE_TIMELINE;
        }

        OperacaoModel itemAtual = listaOperacoes.get(position);

        // Se o item estiver explicitamente marcado como destaque
        if (itemAtual.isDestaque()) {
            return TYPE_DESTAQUE;
        }

        // Verifica se esta posição corresponde ao lançamento futuro mais próximo
        int posicaoMaisProxima = encontrarIndiceFuturoMaisProximo();
        if (position == posicaoMaisProxima) {
            return TYPE_DESTAQUE;
        }

        return TYPE_TIMELINE;
    }

    /**
     * Encontra o índice da operação futura com data mais próxima em relação à data atual do sistema.
     */
    private int encontrarIndiceFuturoMaisProximo() {
        Date agora = new Date();
        int indiceMaisProximo = -1;
        long menorDiferenca = Long.MAX_VALUE;

        for (int i = 0; i < listaOperacoes.size(); i++) {
            OperacaoModel op = listaOperacoes.get(i);
            if (op.getDataLancamento() != null && op.getDataLancamento().after(agora)) {
                long diff = op.getDataLancamento().getTime() - agora.getTime();
                if (diff < menorDiferenca) {
                    menorDiferenca = diff;
                    indiceMaisProximo = i;
                }
            }
        }
        return indiceMaisProximo;
    }

    @NonNull
    @Override
    public RecyclerView.ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        LayoutInflater inflater = LayoutInflater.from(parent.getContext());
        View view = inflater.inflate(R.layout.item_operacao_card, parent, false);
        return new TimelineViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull RecyclerView.ViewHolder holder, int position) {
        OperacaoModel operacao = listaOperacoes.get(position);
        if (holder instanceof TimelineViewHolder) {
            TimelineViewHolder timelineHolder = (TimelineViewHolder) holder;
            if (timelineHolder.tvTitulo != null) timelineHolder.tvTitulo.setText(operacao.getTitulo());
            if (timelineHolder.tvFaseTipo != null) timelineHolder.tvFaseTipo.setText(operacao.getFaseStatus());
            if (timelineHolder.tvData != null) timelineHolder.tvData.setText(operacao.getDataFormatada());
            if (timelineHolder.tvSinopse != null) timelineHolder.tvSinopse.setText(operacao.getSinopse());
        }
    }

    @Override
    public int getItemCount() {
        return listaOperacoes != null ? listaOperacoes.size() : 0;
    }

    // ViewHolder: Card de Operação
    public static class TimelineViewHolder extends RecyclerView.ViewHolder {
        public ImageView ivPoster;
        public TextView tvTitulo;
        public TextView tvFaseTipo;
        public TextView tvData;
        public TextView tvSinopse;

        public TimelineViewHolder(@NonNull View itemView) {
            super(itemView);
            ivPoster = itemView.findViewById(R.id.ivPoster);
            tvTitulo = itemView.findViewById(R.id.tvTitulo);
            tvFaseTipo = itemView.findViewById(R.id.tvFase);
            tvData = itemView.findViewById(R.id.tvData);
            tvSinopse = itemView.findViewById(R.id.tvSinopse);
        }
    }
}
