package com.example.marvel.ui.joias

import android.graphics.Color
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.view.animation.OvershootInterpolator
import androidx.fragment.app.Fragment
import com.example.marvel.databinding.FragmentJoiasBinding
import dagger.hilt.android.AndroidEntryPoint

data class InfinityGem(
    val name: String,
    val color: String,
    val affects: String,
    val power: String,
    val users: String
)

@AndroidEntryPoint
class JoiasFragment : Fragment() {

    private var _binding: FragmentJoiasBinding? = null
    private val binding get() = _binding!!

    // Mesma ordem de gemColors em GemWheelView (0=Power, 1=Space, 2=Reality, 3=Mind, 4=Time, 5=Soul)
    private val gems = listOf(
        InfinityGem("JOIA DO PODER", "#7B00E0",
            "Força, energia e destruição cósmica",
            "Amplifica qualquer força ao nível cósmico. Com ela é possível destruir planetas inteiros com um toque. Potencializa o efeito de todas as outras joias simultaneamente.",
            "Ronan, Senhor das Estrelas, Thanos"),
        InfinityGem("JOIA DO ESPAÇO", "#0055FF",
            "Movimento, localização e portais dimensionais",
            "Permite viajar para qualquer ponto do universo instantaneamente e criar portais entre dimensões. Contida no cubo cósmico chamado Tesseract por séculos.",
            "Odin, Caveira Vermelha, Loki, Thanos"),
        InfinityGem("JOIA DA REALIDADE", "#DD1100",
            "Matéria, leis físicas e ilusão",
            "Altera a realidade à vontade, muda permanentemente as leis da física e transforma o que é real no que não é. Sua forma bruta é o Éter, uma substância líquida.",
            "Malekith, Jane Foster, Thanos"),
        InfinityGem("JOIA DA MENTE", "#FFCC00",
            "Pensamento, memória e controle mental",
            "Amplifica poderes telepáticos e telecinéticos, dando acesso e controle sobre qualquer mente. No cetro de Loki ela deu origem à IA cósmica chamada Visão.",
            "Loki (cetro), Ultron, Visão, Thanos"),
        InfinityGem("JOIA DO TEMPO", "#00BB44",
            "Tempo, cronologia e causalidade",
            "Controla o fluxo do tempo: pode pausar, reverter, acelerar ou criar loops temporais. Guardada pelo Doutor Estranho no Olho de Agamotto para protegê-la de Thanos.",
            "Doutor Estranho, Thanos"),
        InfinityGem("JOIA DA ALMA", "#FF6600",
            "Vida, morte e consciência universal",
            "A mais misteriosa e perigosa das joias. Contém uma dimensão interna chamada Bolso da Alma. Seu portador controla toda forma de vida e morte no universo.",
            "Caveira Vermelha (Guardião), Thanos, Hulk")
    )

    private var currentGemColor: Int = Color.parseColor("#7B00E0")
    private var colorAnimator: android.animation.ValueAnimator? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enterTransition = com.google.android.material.transition.MaterialFadeThrough()
        exitTransition = com.google.android.material.transition.MaterialFadeThrough()
    }

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        _binding = FragmentJoiasBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Mostra a primeira joia (Power) imediatamente
        updateCard(0)

        // Atualiza card quando roda para e uma joia encaixa na frente
        binding.gemWheelView.onGemSelected = { index -> updateCard(index) }

        // TAP na joia → abre em 3D com overlay escuro
        binding.gemWheelView.onGemTapped = { index ->
            updateCard(index)
            expandGem(index)
        }

        // Tap no overlay → fecha
        binding.dimOverlay.setOnClickListener { collapseGem() }
    }

    private fun updateCard(index: Int) {
        val gem = gems[index]
        val targetColor = Color.parseColor(gem.color)

        // Transição suave da cor de acento do card (título, traço decorativo e borda)
        colorAnimator?.cancel()
        val startColor = currentGemColor
        colorAnimator = android.animation.ValueAnimator.ofArgb(startColor, targetColor).apply {
            duration = 300
            addUpdateListener { animator ->
                val animatedColor = animator.animatedValue as Int
                binding.tvGemName.setTextColor(animatedColor)
                binding.dividerGem.setBackgroundColor(animatedColor)
                binding.cardDetails.strokeColor = animatedColor
            }
            start()
        }
        currentGemColor = targetColor

        binding.tvGemName.text = gem.name
        binding.tvGemAffects.text = "AFETA: ${gem.affects.uppercase()}"
        binding.tvGemPower.text = gem.power
        binding.tvGemUsers.text = gem.users

        // Atualização padronizada dos rótulos e métricas S.H.I.E.L.D.
        when (index) {
            0 -> {
                binding.tvLabelRadGamma.text = "EMISSÃO GAMA"
                binding.tvRadGamma.text = "9,87 TeraElectronVolts // Energia Pura"
                binding.tvLabelAmeaca.text = "CLASSIFICAÇÃO DE AMEAÇA"
                binding.tvNivelAmeaca.text = "Classe Ômega // Nível Cósmico"
            }
            1 -> {
                binding.tvLabelRadGamma.text = "DISTORÇÃO ESPACIAL"
                binding.tvRadGamma.text = "100% // Tesseract Ativo"
                binding.tvLabelAmeaca.text = "CLASSIFICAÇÃO DE AMEAÇA"
                binding.tvNivelAmeaca.text = "Classe Ômega // Nível Cósmico"
            }
            2 -> {
                binding.tvLabelRadGamma.text = "ALTERAÇÃO DA MATÉRIA"
                binding.tvRadGamma.text = "Éter Fluido // Transmutação Crítica"
                binding.tvLabelAmeaca.text = "CLASSIFICAÇÃO DE AMEAÇA"
                binding.tvNivelAmeaca.text = "Classe Ômega // Nível Cósmico"
            }
            3 -> {
                binding.tvLabelRadGamma.text = "ONDA NEURAL CÓSMICA"
                binding.tvRadGamma.text = "Protocolo Visão // Frequência Ativa"
                binding.tvLabelAmeaca.text = "CLASSIFICAÇÃO DE AMEAÇA"
                binding.tvNivelAmeaca.text = "Classe Ômega // Nível Cósmico"
            }
            4 -> {
                binding.tvLabelRadGamma.text = "FLUXO TEMPORAL"
                binding.tvRadGamma.text = "Olho de Agamotto // Sincronizado"
                binding.tvLabelAmeaca.text = "CLASSIFICAÇÃO DE AMEAÇA"
                binding.tvNivelAmeaca.text = "Classe Ômega // Nível Cósmico"
            }
            5 -> {
                binding.tvLabelRadGamma.text = "DIMENSÃO INTERIOR"
                binding.tvRadGamma.text = "Bolso da Alma // Vormir Ativo"
                binding.tvLabelAmeaca.text = "CLASSIFICAÇÃO DE AMEAÇA"
                binding.tvNivelAmeaca.text = "Classe Ômega // Nível Cósmico"
            }
        }
    }

    private fun expandGem(index: Int) {
        val gem = gems[index]
        val color = Color.parseColor(gem.color)
        binding.expandedGemView.gemIndex = index
        binding.expandedGemView.gemColor = color

        binding.tvExpandedGemTitle.text = gem.name
        binding.tvExpandedGemTitle.setTextColor(color)

        // Estado inicial para a transição suave
        binding.dimOverlay.alpha = 0f
        binding.dimOverlay.visibility = View.VISIBLE

        binding.tvExpandedGemTitle.alpha = 0f
        binding.tvExpandedGemTitle.visibility = View.VISIBLE

        binding.tvCloseHint.alpha = 0f
        binding.tvCloseHint.visibility = View.VISIBLE

        binding.expandedGemView.scaleX = 0.35f
        binding.expandedGemView.scaleY = 0.35f
        binding.expandedGemView.alpha = 0f
        binding.expandedGemView.visibility = View.VISIBLE

        // Fade in suave do blackout no fundo
        binding.dimOverlay.animate()
            .alpha(1f)
            .setDuration(350)
            .start()

        // Surgimento grandioso da joia 3D
        binding.expandedGemView.animate()
            .scaleX(1f).scaleY(1f).alpha(1f)
            .setDuration(400)
            .setInterpolator(OvershootInterpolator(1.15f))
            .start()

        binding.tvExpandedGemTitle.animate()
            .alpha(1f)
            .setDuration(400)
            .start()

        binding.tvCloseHint.animate()
            .alpha(1f)
            .setDuration(400)
            .start()
    }

    private fun collapseGem() {
        binding.dimOverlay.animate()
            .alpha(0f)
            .setDuration(250)
            .withEndAction {
                binding.dimOverlay.visibility = View.GONE
            }
            .start()

        binding.tvExpandedGemTitle.animate()
            .alpha(0f)
            .setDuration(200)
            .withEndAction {
                binding.tvExpandedGemTitle.visibility = View.GONE
            }
            .start()

        binding.tvCloseHint.animate()
            .alpha(0f)
            .setDuration(200)
            .withEndAction {
                binding.tvCloseHint.visibility = View.GONE
            }
            .start()

        binding.expandedGemView.animate()
            .scaleX(0.25f).scaleY(0.25f).alpha(0f)
            .setDuration(250)
            .withEndAction {
                binding.expandedGemView.visibility = View.GONE
            }
            .start()
    }

    override fun onDestroyView() {
        super.onDestroyView()
        colorAnimator?.cancel()
        colorAnimator = null
        _binding = null
    }
}
