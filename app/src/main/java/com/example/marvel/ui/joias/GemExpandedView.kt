package com.example.marvel.ui.joias

import android.animation.ValueAnimator
import android.annotation.SuppressLint
import android.content.Context
import android.graphics.*
import android.util.AttributeSet
import android.view.MotionEvent
import android.view.VelocityTracker
import android.view.View
import android.view.animation.DecelerateInterpolator
import android.view.animation.LinearInterpolator
import com.example.marvel.R
import kotlin.math.*

/**
 * Visualizador 3D Fotorrealista de Inspeção das Joias do Infinito (S.H.I.E.L.D. Holographic 3D)
 *
 * Características:
 * - Sequências 360° pré-renderizadas em Blender 5.2 (Cycles Raytracing)
 * - Rotação horizontal suave a 360° através de toque e arraste
 * - Inércia física (Fling com desaceleração exponencial ao soltar)
 * - Inclinação de perspectiva 3D vertical (Pitch Parallax com android.graphics.Camera)
 * - Halo cósmico e pulsação quântica em repouso (Idle breathing)
 * - HUD tático holográfico da S.H.I.E.L.D. com mira angular e indicadores
 */
class GemExpandedView @JvmOverloads constructor(
    context: Context, attrs: AttributeSet? = null
) : View(context, attrs) {

    // Nomes dos drawables por joia (16 frames por joia)
    private val gemPrefixes = arrayOf("power", "space", "reality", "mind", "time", "soul")

    var gemColor: Int = Color.parseColor("#7B00E0")
        set(value) {
            field = value
            invalidate()
        }

    var gemIndex: Int = 0
        set(value) {
            if (field != value || activeBitmaps == null) {
                field = value.coerceIn(0, 5)
                loadGemBitmaps(field)
                invalidate()
            }
        }

    private val NUM_FRAMES = 24

    // Cache dos 24 bitmaps da joia ativa para rotação ultra suave a 360° (60-120 FPS)
    private var activeBitmaps: Array<Bitmap?>? = null

    // Ângulo de rotação horizontal contínuo (0f a 360f)
    var rotationAngle: Float = 0f
        private set

    // Inclinação vertical de perspectiva (-22f a 22f)
    private var tiltPitch: Float = 0f

    // Flutuação idle
    private var idlePhase: Float = 0f

    // Estado do toque
    private var lastTouchX = 0f
    private var lastTouchY = 0f
    private var velocityTracker: VelocityTracker? = null
    private var flingAnimator: ValueAnimator? = null
    private var idleAnimator: ValueAnimator? = null

    // Utilitários de desenho
    private val paint = Paint(Paint.ANTI_ALIAS_FLAG or Paint.FILTER_BITMAP_FLAG)
    private val glowPaint = Paint(Paint.ANTI_ALIAS_FLAG)
    private val hudPaint = Paint(Paint.ANTI_ALIAS_FLAG)
    private val textPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        typeface = Typeface.create("sans-serif-condensed", Typeface.BOLD)
        textSize = 28f
        color = Color.parseColor("#00E5FF")
        textAlign = Paint.Align.CENTER
    }

    private val camera3D = Camera()
    private val drawMatrix = Matrix()

    init {
        loadGemBitmaps(0)
        startIdleAnimation()
    }

    private fun loadGemBitmaps(index: Int) {
        val prefix = gemPrefixes[index]
        val bitmaps = arrayOfNulls<Bitmap>(NUM_FRAMES)
        val resources = context.resources
        val packageName = context.packageName

        for (f in 0 until NUM_FRAMES) {
            val resName = String.format("gem_%s_%02d", prefix, f)
            val resId = resources.getIdentifier(resName, "drawable", packageName)
            if (resId != 0) {
                try {
                    bitmaps[f] = BitmapFactory.decodeResource(resources, resId)
                } catch (e: Exception) {
                    bitmaps[f] = null
                }
            }
        }
        activeBitmaps = bitmaps
    }

    private fun startIdleAnimation() {
        idleAnimator?.cancel()
        idleAnimator = ValueAnimator.ofFloat(0f, (2 * Math.PI).toFloat()).apply {
            duration = 4000
            repeatCount = ValueAnimator.INFINITE
            interpolator = LinearInterpolator()
            addUpdateListener {
                idlePhase = it.animatedValue as Float
                // Leve rotação contínua quando ociosa (0.1 graus por frame)
                if (velocityTracker == null && flingAnimator?.isRunning != true) {
                    rotationAngle = (rotationAngle + 0.15f) % 360f
                }
                invalidate()
            }
            start()
        }
    }

    @SuppressLint("ClickableViewAccessibility")
    override fun onTouchEvent(event: MotionEvent): Boolean {
        if (velocityTracker == null) {
            velocityTracker = VelocityTracker.obtain()
        }
        velocityTracker?.addMovement(event)

        when (event.actionMasked) {
            MotionEvent.ACTION_DOWN -> {
                flingAnimator?.cancel()
                lastTouchX = event.x
                lastTouchY = event.y
                return true
            }

            MotionEvent.ACTION_MOVE -> {
                val dx = event.x - lastTouchX
                val dy = event.y - lastTouchY

                // Rotação horizontal 360° responsiva
                rotationAngle = (rotationAngle - dx * 0.55f)
                if (rotationAngle < 0f) rotationAngle += 360f
                if (rotationAngle >= 360f) rotationAngle %= 360f

                // Inclinação vertical limitada para realismo tridimensional
                tiltPitch = (tiltPitch - dy * 0.25f).coerceIn(-22f, 22f)

                lastTouchX = event.x
                lastTouchY = event.y
                invalidate()
            }

            MotionEvent.ACTION_UP, MotionEvent.ACTION_CANCEL -> {
                velocityTracker?.computeCurrentVelocity(1000)
                val vx = velocityTracker?.xVelocity ?: 0f
                velocityTracker?.recycle()
                velocityTracker = null

                // Se houver velocidade suficiente, inicia o giro por inércia
                if (abs(vx) > 150f) {
                    startFling(vx)
                } else {
                    // Retorna suavemente o tilt para a posição neutra
                    settleTilt()
                }
            }
        }
        return true
    }

    private fun startFling(initialVelocity: Float) {
        flingAnimator?.cancel()
        val durationMs = (abs(initialVelocity) * 0.8f).coerceIn(400f, 1800f).toLong()
        val totalDeltaAngle = -initialVelocity * 0.45f

        val startAngle = rotationAngle
        flingAnimator = ValueAnimator.ofFloat(0f, 1f).apply {
            duration = durationMs
            interpolator = DecelerateInterpolator(1.8f)
            addUpdateListener { anim ->
                val progress = anim.animatedValue as Float
                rotationAngle = (startAngle + totalDeltaAngle * progress)
                if (rotationAngle < 0f) rotationAngle = (rotationAngle % 360f) + 360f
                if (rotationAngle >= 360f) rotationAngle %= 360f
                invalidate()
            }
            start()
        }
        settleTilt()
    }

    private fun settleTilt() {
        ValueAnimator.ofFloat(tiltPitch, 0f).apply {
            duration = 350
            interpolator = DecelerateInterpolator()
            addUpdateListener {
                tiltPitch = it.animatedValue as Float
                invalidate()
            }
            start()
        }
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)

        val w = width.toFloat()
        val h = height.toFloat()
        if (w <= 0f || h <= 0f) return

        val cx = w / 2f
        val cy = h / 2f
        val hoverY = sin(idlePhase) * 6f // Flutuação levitante quântica

        // 1. Halo Cósmico de Energia (Radial Glow)
        val pulse = 0.85f + 0.15f * sin(idlePhase * 1.5f)
        val glowRadius = w * 0.45f * pulse
        val r = Color.red(gemColor)
        val g = Color.green(gemColor)
        val b = Color.blue(gemColor)

        val glowColors = intArrayOf(
            Color.argb((110 * pulse).toInt().coerceIn(0, 255), r, g, b),
            Color.argb((35 * pulse).toInt().coerceIn(0, 255), r, g, b),
            Color.TRANSPARENT
        )
        val glowPositions = floatArrayOf(0f, 0.55f, 1f)
        glowPaint.shader = RadialGradient(cx, cy + hoverY, glowRadius, glowColors, glowPositions, Shader.TileMode.CLAMP)
        canvas.drawCircle(cx, cy + hoverY, glowRadius, glowPaint)

        // 2. Anéis de Contenção Holográfica S.H.I.E.L.D.
        hudPaint.style = Paint.Style.STROKE
        hudPaint.strokeWidth = 1.8f
        hudPaint.color = Color.parseColor("#3300E5FF") // Cyan translúcido
        canvas.drawCircle(cx, cy + hoverY, w * 0.44f, hudPaint)

        // Marcas de calibração orbital
        hudPaint.strokeWidth = 2.5f
        hudPaint.color = Color.parseColor("#6600E5FF")
        val ringR = w * 0.44f
        for (i in 0 until 8) {
            val ang = Math.toRadians((i * 45.0 + rotationAngle * 0.5))
            val x1 = cx + (ringR - 6f) * cos(ang).toFloat()
            val y1 = (cy + hoverY) + (ringR - 6f) * sin(ang).toFloat()
            val x2 = cx + (ringR + 6f) * cos(ang).toFloat()
            val y2 = (cy + hoverY) + (ringR + 6f) * sin(ang).toFloat()
            canvas.drawLine(x1, y1, x2, y2, hudPaint)
        }

        // 3. Renderização 3D da Joia
        val bitmaps = activeBitmaps
        if (bitmaps != null) {
            // Calcula o frame correspondente ao ângulo de 360° (24 frames)
            val normalizedAngle = ((rotationAngle % 360f) + 360f) % 360f
            val frameIndex = ((normalizedAngle / 360f) * NUM_FRAMES).toInt().coerceIn(0, NUM_FRAMES - 1)
            val bmp = bitmaps[frameIndex]

            if (bmp != null && !bmp.isRecycled) {
                canvas.save()

                // Matriz 3D de inclinação de perspectiva
                camera3D.save()
                camera3D.rotateX(tiltPitch)
                camera3D.getMatrix(drawMatrix)
                camera3D.restore()

                // Centraliza a transformação
                drawMatrix.preTranslate(-bmp.width / 2f, -bmp.height / 2f)
                val scale = (w * 0.80f) / bmp.width.toFloat()
                drawMatrix.postScale(scale, scale)
                drawMatrix.postTranslate(cx, cy + hoverY)

                canvas.concat(drawMatrix)
                canvas.drawBitmap(bmp, 0f, 0f, paint)
                canvas.restore()
            }
        }

        // 4. Cantoneiras Táticas de Mira S.H.I.E.L.D.
        val boxR = w * 0.38f
        hudPaint.color = Color.parseColor("#8000E5FF")
        hudPaint.strokeWidth = 2f
        val cornerLen = 14f

        // Top-Left
        canvas.drawLine(cx - boxR, cy - boxR + hoverY, cx - boxR + cornerLen, cy - boxR + hoverY, hudPaint)
        canvas.drawLine(cx - boxR, cy - boxR + hoverY, cx - boxR, cy - boxR + cornerLen + hoverY, hudPaint)
        // Top-Right
        canvas.drawLine(cx + boxR, cy - boxR + hoverY, cx + boxR - cornerLen, cy - boxR + hoverY, hudPaint)
        canvas.drawLine(cx + boxR, cy - boxR + hoverY, cx + boxR, cy - boxR + cornerLen + hoverY, hudPaint)
        // Bottom-Left
        canvas.drawLine(cx - boxR, cy + boxR + hoverY, cx - boxR + cornerLen, cy + boxR + hoverY, hudPaint)
        canvas.drawLine(cx - boxR, cy + boxR + hoverY, cx - boxR, cy + boxR - cornerLen + hoverY, hudPaint)
        // Bottom-Right
        canvas.drawLine(cx + boxR, cy + boxR + hoverY, cx + boxR - cornerLen, cy + boxR + hoverY, hudPaint)
        canvas.drawLine(cx + boxR, cy + boxR + hoverY, cx + boxR, cy + boxR - cornerLen + hoverY, hudPaint)

        // 5. Indicador Holográfico de Ângulo
        val degText = String.format("ESTABILIDADE 3D: %.0f° · BLENDER CYCLES", rotationAngle)
        textPaint.color = Color.parseColor("#CC00E5FF")
        canvas.drawText(degText, cx, h - 8f, textPaint)
    }

    override fun onDetachedFromWindow() {
        super.onDetachedFromWindow()
        idleAnimator?.cancel()
        flingAnimator?.cancel()
    }
}
