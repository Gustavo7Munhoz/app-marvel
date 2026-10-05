package com.example.marvel.ui.joias

import android.animation.Animator
import android.animation.AnimatorListenerAdapter
import android.animation.ValueAnimator
import android.content.Context
import android.graphics.*
import android.util.AttributeSet
import android.view.MotionEvent
import android.view.View
import android.view.animation.DecelerateInterpolator
import kotlin.math.*

class GemWheelView @JvmOverloads constructor(
    context: Context, attrs: AttributeSet? = null
) : View(context, attrs) {

    // MCU canonical colors
    val gemColors = intArrayOf(
        0xFF7B00E0.toInt(),  // 0 Power — Roxo vibrante
        0xFF0055FF.toInt(),  // 1 Space — Azul
        0xFFDD1100.toInt(),  // 2 Reality — Vermelho
        0xFFFFCC00.toInt(),  // 3 Mind — Amarelo/Dourado
        0xFF00BB44.toInt(),  // 4 Time — Verde
        0xFFFF6600.toInt(),  // 5 Soul — Laranja
    )

    private val NUM_GEMS = 6
    var onGemSelected: ((Int) -> Unit)? = null
    var onGemTapped: ((Int) -> Unit)? = null

    private var rotationAngle = 90f
    private var lastX = 0f
    private var downX = 0f
    private var downY = 0f
    private var snapAnimator: ValueAnimator? = null
    private val paint = Paint(Paint.ANTI_ALIAS_FLAG)

    override fun onTouchEvent(event: MotionEvent): Boolean {
        when (event.action) {
            MotionEvent.ACTION_DOWN -> {
                snapAnimator?.cancel()
                lastX = event.x; downX = event.x; downY = event.y
                return true
            }
            MotionEvent.ACTION_MOVE -> {
                rotationAngle += (event.x - lastX) * 0.55f
                lastX = event.x
                invalidate()
            }
            MotionEvent.ACTION_UP -> {
                val dist = sqrt((event.x - downX).pow(2) + (event.y - downY).pow(2))
                if (dist < 20f) {
                    val idx = getFrontGemIndex()
                    onGemTapped?.invoke(idx)
                } else {
                    snapToNearest()
                }
            }
        }
        return true
    }

    fun getFrontGemIndex(): Int {
        val step = 360f / NUM_GEMS
        val snapped = (round((rotationAngle - 90f) / step) * step) + 90f
        val steps = ((90f - snapped) / step).roundToInt()
        return ((steps % NUM_GEMS) + NUM_GEMS) % NUM_GEMS
    }

    private fun snapToNearest() {
        val step = 360f / NUM_GEMS
        val snapped = (round((rotationAngle - 90f) / step) * step) + 90f
        snapAnimator = ValueAnimator.ofFloat(rotationAngle, snapped).apply {
            duration = 350; interpolator = DecelerateInterpolator()
            addUpdateListener { rotationAngle = it.animatedValue as Float; invalidate() }
            addListener(object : AnimatorListenerAdapter() {
                override fun onAnimationEnd(animation: Animator) {
                    onGemSelected?.invoke(getFrontGemIndex())
                }
            })
            start()
        }
    }

    private val gemBitmaps = arrayOfNulls<Bitmap>(NUM_GEMS)
    private val gemPrefixes = arrayOf("power", "space", "reality", "mind", "time", "soul")
    private val matrix = Matrix()
    private val hudPaint = Paint(Paint.ANTI_ALIAS_FLAG)

    init {
        loadBitmaps()
    }

    private fun loadBitmaps() {
        val res = context.resources
        val pkg = context.packageName
        for (i in 0 until NUM_GEMS) {
            val resName = "gem_${gemPrefixes[i]}_00"
            val resId = res.getIdentifier(resName, "drawable", pkg)
            if (resId != 0) {
                try {
                    gemBitmaps[i] = BitmapFactory.decodeResource(res, resId)
                } catch (_: Exception) {}
            }
        }
    }

    override fun onDraw(canvas: Canvas) {
        val cx = width / 2f
        val cy = height * 0.50f
        val orbitX = width * 0.38f
        val orbitY = height * 0.22f

        // 1. Linha Orbital Holográfica S.H.I.E.L.D. (sutil e discreta)
        hudPaint.style = Paint.Style.STROKE
        hudPaint.strokeWidth = 1.5f
        hudPaint.color = Color.parseColor("#1FFFFFFF")
        canvas.drawOval(cx - orbitX, cy - orbitY, cx + orbitX, cy + orbitY, hudPaint)

        // 2. Ordenação de profundidade (Painter's Algorithm)
        (0 until NUM_GEMS)
            .sortedBy { sin(Math.toRadians((rotationAngle + it * 60.0))) }
            .forEach { i ->
                val rad = Math.toRadians((rotationAngle + i * 60.0))
                val x = cx + orbitX * cos(rad).toFloat()
                val y = cy + orbitY * sin(rad).toFloat()
                val depth = ((sin(rad) + 1f) / 2f).toFloat()

                val bmp = gemBitmaps[i]
                val r = Color.red(gemColors[i])
                val g = Color.green(gemColors[i])
                val b = Color.blue(gemColors[i])

                if (bmp != null && !bmp.isRecycled) {
                    val size = width * 0.22f * (0.52f + 0.48f * depth)

                    // BRILHO (GLOW) EXCLUSIVAMENTE NA JOIA CENTRAL (depth > 0.85f)
                    if (depth > 0.85f) {
                        val frontRatio = ((depth - 0.85f) / 0.15f).coerceIn(0f, 1f)
                        paint.reset()
                        paint.isAntiAlias = true
                        paint.style = Paint.Style.FILL
                        val glowR = size * 0.95f
                        val glowColors = intArrayOf(
                            Color.argb((160 * frontRatio).toInt().coerceIn(0, 255), r, g, b),
                            Color.TRANSPARENT
                        )
                        paint.shader = RadialGradient(x, y, glowR, glowColors, floatArrayOf(0f, 1f), Shader.TileMode.CLAMP)
                        canvas.drawCircle(x, y, glowR, paint)
                    }

                    // Renderização da Joia 3D (Blender Cycles)
                    matrix.reset()
                    matrix.postTranslate(-bmp.width / 2f, -bmp.height / 2f)
                    val scale = size / bmp.width.toFloat()
                    matrix.postScale(scale, scale)
                    matrix.postTranslate(x, y)

                    paint.reset()
                    paint.isAntiAlias = true
                    paint.isFilterBitmap = true
                    // Alpha mínimo de 0.60 (153/255) para que as joias laterais nunca sumam
                    paint.alpha = (153 + (102 * depth)).toInt().coerceIn(153, 255)
                    canvas.drawBitmap(bmp, matrix, paint)

                    // Retículo na joia central com a cor da própria joia
                    if (depth > 0.94f) {
                        hudPaint.color = Color.argb(160, r, g, b)
                        hudPaint.strokeWidth = 1.8f
                        canvas.drawCircle(x, y, size * 0.65f, hudPaint)
                    }
                } else {
                    // Fallback
                    val rX = width * 0.10f * (0.48f + 0.52f * depth)
                    val rY = rX * 1.3f
                    val alpha = (0.60f + 0.40f * depth).coerceIn(0.60f, 1.0f)
                    drawGem(canvas, x, y, rX, rY, gemColors[i], alpha, isCentral = (depth > 0.85f))
                }
            }
    }

    /** Draws a realistic faceted oval infinity gem (cushion cut style) */
    fun drawGem(canvas: Canvas, cx: Float, cy: Float, rX: Float, rY: Float, color: Int, alpha: Float, isCentral: Boolean = false) {
        val a = (alpha * 255).toInt().coerceIn(0, 255)
        val r = Color.red(color); val g = Color.green(color); val b = Color.blue(color)

        // ── Multi-ring energy glow apenas se for a joia central ──────────────
        if (isCentral) {
            paint.reset(); paint.isAntiAlias = true; paint.style = Paint.Style.FILL
            val glows = listOf(2.4f to 0.12f, 1.6f to 0.25f)
            for ((sc, af) in glows) {
                paint.color = Color.argb((a * af).toInt(), r, g, b)
                paint.maskFilter = BlurMaskFilter(rX * sc * 0.5f, BlurMaskFilter.Blur.NORMAL)
                canvas.drawOval(cx - rX * sc, cy - rY * sc, cx + rX * sc, cy + rY * sc, paint)
            }
            paint.maskFilter = null
        }

        // ── Base oval (very dark version of color) ───────────────────────────
        paint.color = Color.argb(a, (r * 0.15f).toInt(), (g * 0.15f).toInt(), (b * 0.15f).toInt())
        canvas.drawOval(cx - rX, cy - rY, cx + rX, cy + rY, paint)

        // ── 8 Crown facets (cushion cut — trapezoids from inner oval to girdle) ──
        val nFacets = 8
        val tableR = 0.40f // inner oval radius ratio
        for (i in 0 until nFacets) {
            val offset = -Math.PI / nFacets // rotate facets so edges align with cardinal
            val a1 = offset + i * Math.PI * 2 / nFacets
            val a2 = offset + (i + 1) * Math.PI * 2 / nFacets
            val mid = (a1 + a2) / 2.0

            // Inner table corners
            val tx1 = cx + rX * tableR * cos(a1).toFloat()
            val ty1 = cy + rY * tableR * sin(a1).toFloat()
            val tx2 = cx + rX * tableR * cos(a2).toFloat()
            val ty2 = cy + rY * tableR * sin(a2).toFloat()
            // Outer girdle corners
            val gx1 = cx + rX * 0.97f * cos(a1).toFloat()
            val gy1 = cy + rY * 0.97f * sin(a1).toFloat()
            val gx2 = cx + rX * 0.97f * cos(a2).toFloat()
            val gy2 = cy + rY * 0.97f * sin(a2).toFloat()

            val path = Path().apply {
                moveTo(tx1, ty1); lineTo(gx1, gy1); lineTo(gx2, gy2); lineTo(tx2, ty2); close()
            }

            // Light source top-left → facets at ~315° get brighter
            val lightDot = ((cos(mid - Math.PI * 1.25) + 1.0) / 2.0).toFloat()
            val altB = if (i % 2 == 0) 0.92f else 0.62f
            val shade = lightDot * 0.6f + altB * 0.4f
            val blend = 0.15f

            paint.style = Paint.Style.FILL
            paint.color = Color.argb(a,
                (r * shade + 255 * blend * shade).toInt().coerceIn(0, 255),
                (g * shade + 255 * blend * shade).toInt().coerceIn(0, 255),
                (b * shade + 255 * blend * shade).toInt().coerceIn(0, 255))
            canvas.drawPath(path, paint)

            // Facet edge lines (subtle white)
            paint.style = Paint.Style.STROKE
            paint.strokeWidth = 1.3f
            paint.color = Color.argb((a * 0.28f).toInt(), 255, 255, 255)
            canvas.drawPath(path, paint)
        }

        // ── 8 Star facets (triangles from table edge to inner edge of crown) ──
        for (i in 0 until nFacets) {
            val offset = 0.0
            val tipAngle = offset + i * Math.PI * 2 / nFacets
            val lAngle = tipAngle - Math.PI / nFacets
            val rAngle = tipAngle + Math.PI / nFacets

            val tipX = cx + rX * tableR * cos(tipAngle).toFloat()
            val tipY = cy + rY * tableR * sin(tipAngle).toFloat()
            val innerR = tableR * 0.55f
            val lx = cx + rX * innerR * cos(lAngle).toFloat()
            val ly = cy + rY * innerR * sin(lAngle).toFloat()
            val rx2 = cx + rX * innerR * cos(rAngle).toFloat()
            val ry2 = cy + rY * innerR * sin(rAngle).toFloat()

            val path = Path().apply { moveTo(tipX, tipY); lineTo(lx, ly); lineTo(rx2, ry2); close() }

            val lightDot = ((cos(tipAngle - Math.PI * 1.25) + 1.0) / 2.0).toFloat()
            val shade = 0.5f + lightDot * 0.5f
            paint.style = Paint.Style.FILL
            paint.color = Color.argb(a,
                min(255, (r * shade * 1.5f).toInt()),
                min(255, (g * shade * 1.5f).toInt()),
                min(255, (b * shade * 1.5f).toInt()))
            canvas.drawPath(path, paint)

            paint.style = Paint.Style.STROKE
            paint.strokeWidth = 1f
            paint.color = Color.argb((a * 0.2f).toInt(), 255, 255, 255)
            canvas.drawPath(path, paint)
        }

        // ── Central table: super bright radial glow (the "heart" of the gem) ──
        paint.style = Paint.Style.FILL
        paint.shader = RadialGradient(cx, cy, rX * 0.42f,
            intArrayOf(
                Color.argb(a, 255, 255, 255),
                Color.argb(a, min(255, r + 100), min(255, g + 100), min(255, b + 100)),
                Color.argb(a, r, g, b),
                Color.argb((a * 0.6f).toInt(), (r * 0.5f).toInt(), (g * 0.5f).toInt(), (b * 0.5f).toInt())
            ),
            floatArrayOf(0f, 0.3f, 0.65f, 1f),
            Shader.TileMode.CLAMP)
        canvas.drawOval(cx - rX * 0.42f, cy - rY * 0.42f, cx + rX * 0.42f, cy + rY * 0.42f, paint)
        paint.shader = null

        // ── Top-left specular highlight (glare on the gem surface) ───────────
        val hlPaint = Paint(Paint.ANTI_ALIAS_FLAG)
        hlPaint.style = Paint.Style.FILL
        hlPaint.shader = RadialGradient(
            cx - rX * 0.18f, cy - rY * 0.42f, rX * 0.48f,
            intArrayOf(Color.argb((a * 0.8f).toInt(), 255, 255, 255), Color.TRANSPARENT),
            null, Shader.TileMode.CLAMP)
        canvas.drawOval(cx - rX * 0.65f, cy - rY * 0.9f, cx + rX * 0.38f, cy + rY * 0.05f, hlPaint)

        // ── Sparkle star ─────────────────────────────────────────────────────
        val sx = cx - rX * 0.17f; val sy = cy - rY * 0.47f
        paint.style = Paint.Style.FILL
        paint.color = Color.argb(a, 255, 255, 255)
        canvas.drawCircle(sx, sy, rX * 0.09f, paint)
        paint.style = Paint.Style.STROKE
        paint.strokeWidth = rX * 0.04f
        val sl = rX * 0.3f
        canvas.drawLine(sx, sy - sl, sx, sy + sl, paint)       // vertical
        canvas.drawLine(sx - sl * 0.7f, sy, sx + sl * 0.7f, sy, paint) // horizontal
        // Diagonal sparkle arms
        paint.strokeWidth = rX * 0.025f
        val sd = sl * 0.5f
        canvas.drawLine(sx - sd, sy - sd, sx + sd, sy + sd, paint)
        canvas.drawLine(sx + sd, sy - sd, sx - sd, sy + sd, paint)
    }
}
