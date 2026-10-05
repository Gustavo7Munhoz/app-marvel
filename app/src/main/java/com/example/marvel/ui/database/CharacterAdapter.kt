package com.example.marvel.ui.database

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.bumptech.glide.Glide
import com.bumptech.glide.load.engine.DiskCacheStrategy
import com.example.marvel.databinding.ItemCharacterCardBinding
import com.example.marvel.domain.model.Character

class CharacterAdapter(
    private val onItemClicked: (Character) -> Unit
) : ListAdapter<Character, CharacterAdapter.CharacterViewHolder>(CharacterDiffCallback()) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): CharacterViewHolder {
        val binding = ItemCharacterCardBinding.inflate(
            LayoutInflater.from(parent.context), parent, false
        )
        return CharacterViewHolder(binding, onItemClicked)
    }

    override fun onBindViewHolder(holder: CharacterViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    class CharacterViewHolder(
        private val binding: ItemCharacterCardBinding,
        private val onItemClicked: (Character) -> Unit
    ) : RecyclerView.ViewHolder(binding.root) {

        fun bind(character: Character) {
            binding.tvName.text = character.name
            binding.tvAlias.text = character.realName.ifEmpty { "CLASSIFIED" }
            binding.tvIdPasta.text = "FILE #${character.id}"
            
            Glide.with(binding.root.context)
                .load(character.imageUrl)
                .diskCacheStrategy(DiskCacheStrategy.ALL)
                .placeholder(android.R.color.darker_gray)
                .error(android.R.color.holo_red_dark)
                .into(binding.ivThumbnail)

            val clickListener = { onItemClicked(character) }
            binding.root.setOnClickListener { clickListener() }
            binding.cardBody.setOnClickListener { clickListener() }
        }
    }

    class CharacterDiffCallback : DiffUtil.ItemCallback<Character>() {
        override fun areItemsTheSame(oldItem: Character, newItem: Character): Boolean {
            return oldItem.id == newItem.id
        }

        override fun areContentsTheSame(oldItem: Character, newItem: Character): Boolean {
            return oldItem == newItem
        }
    }
}
