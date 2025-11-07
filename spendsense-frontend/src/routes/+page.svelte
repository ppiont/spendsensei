<script lang="ts">
	import { BarChart3, Lightbulb, GraduationCap } from '@lucide/svelte';
</script>

<div class="landing-page">
	<!-- Decorative Background Blob -->
	<svg class="background-blob" viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">
		<defs>
			<linearGradient id="blobGradient" x1="0%" y1="0%" x2="100%" y2="100%">
				<stop offset="0%" style="stop-color:#dbeafe;stop-opacity:0.4" />
				<stop offset="100%" style="stop-color:#e0e7ff;stop-opacity:0.3" />
			</linearGradient>
		</defs>
		<path
			fill="url(#blobGradient)"
			d="M450,300 Q550,250 600,350 T700,400 Q650,500 550,480 T400,450 Q350,400 400,320 T450,300Z"
		/>
	</svg>

	<div class="landing-container">
		<div class="landing-content">
			<!-- App Name -->
			<h1 class="landing-title">SpendSense</h1>

			<!-- Hero Card -->
			<div class="hero-card">
				<p class="landing-tagline">
					Financial Clarity,<br />
					Simply Presented
				</p>

				<a href="/dashboard" class="landing-cta">
					View Dashboard
				</a>
			</div>

			<!-- Feature Pills -->
			<div class="feature-pills">
				<div class="feature-pill">
					<BarChart3 class="feature-icon" />
					<span class="feature-label">Track</span>
				</div>
				<div class="feature-pill">
					<Lightbulb class="feature-icon" />
					<span class="feature-label">Insights</span>
				</div>
				<div class="feature-pill">
					<GraduationCap class="feature-icon" />
					<span class="feature-label">Learn</span>
				</div>
			</div>
		</div>
	</div>
</div>

<style>
	.landing-page {
		min-height: 100vh;
		display: flex;
		align-items: center;
		justify-content: center;
		background: linear-gradient(135deg, #eff6ff 0%, #faf5ff 100%);
		padding: 2rem;
		position: relative;
		overflow: hidden;
	}

	.background-blob {
		position: absolute;
		top: 10%;
		right: -10%;
		width: 50%;
		height: auto;
		opacity: 0.6;
		pointer-events: none;
		animation: float 20s ease-in-out infinite;
	}

	@keyframes float {
		0%,
		100% {
			transform: translate(0, 0) rotate(0deg);
		}
		33% {
			transform: translate(30px, -30px) rotate(5deg);
		}
		66% {
			transform: translate(-20px, 20px) rotate(-5deg);
		}
	}

	.landing-container {
		width: 100%;
		max-width: 650px;
		margin: 0 auto;
		position: relative;
		z-index: 1;
	}

	.landing-content {
		text-align: center;
		display: flex;
		flex-direction: column;
		gap: 2.5rem;
	}

	.landing-title {
		font-size: 2.5rem;
		font-weight: 700;
		color: #1f2937;
		letter-spacing: -0.02em;
		margin: 0;
	}

	.hero-card {
		background: white;
		border-radius: 1.5rem;
		padding: 3rem 2.5rem;
		box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.05), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
		display: flex;
		flex-direction: column;
		gap: 2rem;
		transition: all 300ms ease;
	}

	.hero-card:hover {
		box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.1);
		transform: translateY(-4px);
	}

	.landing-tagline {
		font-size: 1.75rem;
		font-weight: 500;
		color: #374151;
		line-height: 1.4;
		margin: 0;
	}

	.landing-cta {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		padding: 1rem 2.5rem;
		font-size: 1rem;
		font-weight: 600;
		color: white;
		background: linear-gradient(to right, #3b82f6, #60a5fa);
		border-radius: 0.75rem;
		text-decoration: none;
		transition: all 200ms ease;
		box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.15), 0 2px 4px -2px rgba(59, 130, 246, 0.15);
		margin: 0 auto;
	}

	.landing-cta:hover {
		transform: translateY(-2px);
		box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.25), 0 4px 6px -4px rgba(59, 130, 246, 0.25);
		background: linear-gradient(to right, #2563eb, #3b82f6);
	}

	.feature-pills {
		display: flex;
		gap: 1rem;
		justify-content: center;
		flex-wrap: wrap;
	}

	.feature-pill {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.75rem 1.5rem;
		background: white;
		border-radius: 9999px;
		box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1);
		transition: all 200ms ease;
	}

	.feature-pill:hover {
		transform: translateY(-2px);
		box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
	}

	:global(.feature-icon) {
		width: 1.25rem;
		height: 1.25rem;
		color: #3b82f6;
		flex-shrink: 0;
	}

	.feature-label {
		font-size: 0.875rem;
		font-weight: 500;
		color: #6b7280;
	}

	/* Responsive */
	@media (max-width: 640px) {
		.landing-title {
			font-size: 2rem;
		}

		.hero-card {
			padding: 2rem 1.5rem;
		}

		.landing-tagline {
			font-size: 1.25rem;
		}

		.landing-content {
			gap: 2rem;
		}

		.background-blob {
			width: 70%;
			right: -20%;
		}

		.feature-pills {
			gap: 0.75rem;
		}

		.feature-pill {
			padding: 0.625rem 1.25rem;
		}
	}
</style>
