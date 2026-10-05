package com.example.marvel.adapter;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.TextView;
import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;
import com.bumptech.glide.Glide;
import com.bumptech.glide.load.engine.DiskCacheStrategy;
import com.example.marvel.R;
import com.example.marvel.network.CharacterModel;
import java.util.List;

/**
 * Adapter para a lista de Dossiês confidenciais da S.H.I.E.L.D.
 */
public class PersonagemAdapter extends RecyclerView.Adapter<PersonagemAdapter.PersonagemViewHolder> {

    private List<CharacterModel> lista;
    private OnPersonagemClickListener listener;

    public interface OnPersonagemClickListener {
        void onPersonagemClick(CharacterModel character);
    }

    public PersonagemAdapter(List<CharacterModel> lista) {
        this.lista = lista;
    }

    public PersonagemAdapter(List<CharacterModel> lista, OnPersonagemClickListener listener) {
        this.lista = lista;
        this.listener = listener;
    }

    public void setLista(List<CharacterModel> novaLista) {
        this.lista = novaLista;
        notifyDataSetChanged();
    }

    @NonNull
    @Override
    public PersonagemViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.item_personagem, parent, false);
        return new PersonagemViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull PersonagemViewHolder holder, int position) {
        CharacterModel item = lista.get(position);
        holder.tvNome.setText(item.getName() != null ? item.getName().toUpperCase() : "CLASSIFICADO");
        holder.tvAlias.setText(item.getDescription() != null && !item.getDescription().isEmpty()
                ? item.getDescription()
                : "REGISTRO CONFIDENCIAL // NÍVEL 7");

        if (item.getImageUrl() != null && !item.getImageUrl().isEmpty()) {
            Glide.with(holder.itemView.getContext())
                    .load(item.getImageUrl())
                    .diskCacheStrategy(DiskCacheStrategy.ALL)
                    .placeholder(android.R.color.darker_gray)
                    .error(android.R.color.holo_red_dark)
                    .into(holder.ivFoto);
        } else {
            holder.ivFoto.setImageResource(android.R.color.darker_gray);
        }

        holder.itemView.setOnClickListener(v -> {
            if (listener != null) {
                listener.onPersonagemClick(item);
            }
        });
    }

    @Override
    public int getItemCount() {
        return lista != null ? lista.size() : 0;
    }

    public static class PersonagemViewHolder extends RecyclerView.ViewHolder {
        public ImageView ivFoto;
        public TextView tvNome;
        public TextView tvAlias;
        public TextView tvIdPasta;

        public PersonagemViewHolder(@NonNull View itemView) {
            super(itemView);
            ivFoto = itemView.findViewById(R.id.ivThumbnail);
            tvNome = itemView.findViewById(R.id.tvName);
            tvAlias = itemView.findViewById(R.id.tvAlias);
            tvIdPasta = itemView.findViewById(R.id.tvIdPasta);
        }
    }
}
