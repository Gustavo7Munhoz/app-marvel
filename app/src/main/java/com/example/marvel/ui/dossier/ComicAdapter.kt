package com.example.marvel.ui.dossier

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.RecyclerView
import com.bumptech.glide.Glide
import com.bumptech.glide.load.engine.DiskCacheStrategy
import com.example.marvel.databinding.ItemComicBinding
import com.example.marvel.domain.model.Comic

class ComicAdapter(private val comics: List<Comic>) : RecyclerView.Adapter<ComicAdapter.ComicViewHolder>() {

    class ComicViewHolder(private val binding: ItemComicBinding) : RecyclerView.ViewHolder(binding.root) {
        fun bind(comic: Comic) {
            binding.tvComicName.text = comic.name
            Glide.with(binding.root.context)
                .load(comic.imageUrl)
                .diskCacheStrategy(DiskCacheStrategy.ALL)
                .into(binding.ivComicCover)
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ComicViewHolder {
        val binding = ItemComicBinding.inflate(LayoutInflater.from(parent.context), parent, false)
        return ComicViewHolder(binding)
    }

    override fun onBindViewHolder(holder: ComicViewHolder, position: Int) {
        holder.bind(comics[position])
    }

    override fun getItemCount() = comics.size
}
