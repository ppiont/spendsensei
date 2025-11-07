<div class="landing-page">
	<div class="landing-container">
		<div class="landing-content">
			<!-- App Name -->
			<h1 class="landing-title">SpendSense</h1>

			<!-- Tagline -->
			<p class="landing-tagline">
				Financial Clarity,<br />
				Simply Presented
			</p>

			<!-- Single CTA -->
			<a href="/dashboard" class="landing-cta">
				View Dashboard
			</a>
		</div>
	</div>
</div>

<style>
	.landing-page {
		min-height: 100vh;
		display: flex;
		align-items: center;
		justify-content: center;
		background: linear-gradient(to bottom right, #eff6ff, #ffffff);
		padding: 2rem;
	}

	.landing-container {
		width: 100%;
		max-width: 600px;
		margin: 0 auto;
	}

	.landing-content {
		text-align: center;
		display: flex;
		flex-direction: column;
		gap: 3rem;
	}

	.landing-title {
		font-size: 3.5rem;
		font-weight: 700;
		color: #1f2937;
		letter-spacing: -0.02em;
		margin: 0;
	}

	.landing-tagline {
		font-size: 1.5rem;
		font-weight: 400;
		color: #6b7280;
		line-height: 1.6;
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
		box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.1),
			0 2px 4px -2px rgba(59, 130, 246, 0.1);
		margin: 0 auto;
	}

	.landing-cta:hover {
		transform: translateY(-2px);
		box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.2),
			0 4px 6px -4px rgba(59, 130, 246, 0.2);
	}

	/* Responsive */
	@media (max-width: 640px) {
		.landing-title {
			font-size: 2.5rem;
		}

		.landing-tagline {
			font-size: 1.25rem;
		}

		.landing-content {
			gap: 2rem;
		}
	}
</style>
