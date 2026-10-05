package com.example.marvel.adapter;

import android.content.Context;
import android.graphics.Color;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.TextView;
import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;
import com.bumptech.glide.Glide;
import com.bumptech.glide.load.engine.DiskCacheStrategy;
import com.bumptech.glide.load.model.GlideUrl;
import com.bumptech.glide.load.model.LazyHeaders;
import com.example.marvel.R;
import com.example.marvel.model.FilmeModel;
import com.google.android.material.card.MaterialCardView;
import java.util.List;

/**
 * Adapter unificado para o Calendário de Operações S.H.I.E.L.D.
 * Utiliza exclusivamente o layout horizontal sóbrio item_operacao_card.xml.
 */
public class FilmeAdapter extends RecyclerView.Adapter<FilmeAdapter.OperacaoViewHolder> {

    private List<FilmeModel> lista;

    public FilmeAdapter(List<FilmeModel> lista) {
        this.lista = lista;
    }

    public void setLista(List<FilmeModel> novaLista) {
        this.lista = novaLista;
        notifyDataSetChanged();
    }

    @NonNull
    @Override
    public OperacaoViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.item_operacao_card, parent, false);
        return new OperacaoViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull OperacaoViewHolder holder, int position) {
        FilmeModel item = lista.get(position);
        Context context = holder.itemView.getContext();

        // 1. Título
        holder.tvTitulo.setText(item.getTitulo());

        // 2. Fase
        holder.tvFase.setText(item.getFaseStatus());

        // 3. Data formatada ("18/12/2026" ou "DATA A DEFINIR")
        String dataStr = item.getDataFormatada();
        if (dataStr == null || dataStr.isEmpty()) {
            dataStr = "DATA A DEFINIR";
        }
        holder.tvData.setText(dataStr);
        if ("DATA A DEFINIR".equalsIgnoreCase(dataStr)) {
            holder.tvData.setTextColor(Color.parseColor("#9A9A9A"));
        } else {
            holder.tvData.setTextColor(Color.parseColor("#EAEAEA"));
        }

        // 4. Sinopse
        holder.tvSinopse.setText(item.getSinopse());

        // 5. Categoria ("CINEMA" ou "DISNEY+")
        String categoria = item.getCategoria();
        holder.tvTagCategoria.setText(categoria != null ? categoria : "MCU");

        // 6. Tratamento visual de destaque exclusivo para o primeiro item (próximo lançamento)
        boolean isPrimeiroItem = (position == 0);
        float density = context.getResources().getDisplayMetrics().density;

        if (isPrimeiroItem) {
            // Borda destacada com acento #F9A825 (1.5dp)
            holder.cardOperacao.setStrokeColor(Color.parseColor("#F9A825"));
            holder.cardOperacao.setStrokeWidth((int) (1.5f * density));

            // Chip de contagem regressiva (ex: "EM 74 DIAS" ou "PRÓXIMO LANÇAMENTO")
            String contagem = item.getContadorRegressivo();
            if (contagem == null || contagem.isEmpty()) {
                contagem = "PRÓXIMO LANÇAMENTO";
            }
            holder.tvBadgeCountdown.setText(contagem);
            holder.tvBadgeCountdown.setVisibility(View.VISIBLE);
        } else {
            // Padrão sóbrio: borda fina #333333 (1dp) e sem chip de contagem
            holder.cardOperacao.setStrokeColor(Color.parseColor("#333333"));
            holder.cardOperacao.setStrokeWidth((int) (1f * density));
            holder.tvBadgeCountdown.setVisibility(View.GONE);
        }

        // 7. Carregamento do pôster via Glide com User-Agent para Wikimedia/Wikipedia
        String posterUrl = item.getPosterUrl();
        Object modelToLoad;
        if (posterUrl != null && !posterUrl.trim().isEmpty()) {
            if (posterUrl.contains("wikimedia.org") || posterUrl.contains("wikipedia.org")) {
                modelToLoad = new GlideUrl(posterUrl, new LazyHeaders.Builder()
                        .addHeader("User-Agent", "MarvelApp/1.0 (android@shield-archive.marvel.internal)")
                        .build());
            } else {
                modelToLoad = posterUrl;
            }
        } else {
            modelToLoad = null;
        }

        Glide.with(context)
                .load(modelToLoad)
                .placeholder(R.drawable.ic_claquete_placeholder)
                .error(R.drawable.ic_claquete_placeholder)
                .diskCacheStrategy(DiskCacheStrategy.ALL)
                .into(holder.ivPoster);
    }

    @Override
    public int getItemCount() {
        return lista != null ? lista.size() : 0;
    }

    public static class OperacaoViewHolder extends RecyclerView.ViewHolder {
        public MaterialCardView cardOperacao;
        public ImageView ivPoster;
        public TextView tvBadgeCountdown;
        public TextView tvTagCategoria;
        public TextView tvTitulo;
        public TextView tvFase;
        public TextView tvData;
        public TextView tvSinopse;

        public OperacaoViewHolder(@NonNull View itemView) {
            super(itemView);
            cardOperacao = itemView.findViewById(R.id.cardOperacao);
            ivPoster = itemView.findViewById(R.id.ivPoster);
            tvBadgeCountdown = itemView.findViewById(R.id.tvBadgeCountdown);
            tvTagCategoria = itemView.findViewById(R.id.tvTagCategoria);
            tvTitulo = itemView.findViewById(R.id.tvTitulo);
            tvFase = itemView.findViewById(R.id.tvFase);
            tvData = itemView.findViewById(R.id.tvData);
            tvSinopse = itemView.findViewById(R.id.tvSinopse);
        }
    }
}
