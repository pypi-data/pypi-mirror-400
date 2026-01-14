<script lang="ts">
	import { onMount } from "svelte";
	import { Gradio } from "@gradio/utils";
	import {
		Block,
		UploadText,
		BlockLabel,
		IconButton,
		IconButtonWrapper,
		Empty,
	} from "@gradio/atoms";
	import { Download, Image as ImageIcon, Clear } from "@gradio/icons";
	import { Upload } from "@gradio/upload";
	import type { TiffEvents, TiffProps, TiffInstance } from "./types";
	import type { FileData } from "@gradio/client";

	// --- CONSTANTS ---
	const TIFF_LIB_URL =
		"https://cdn.jsdelivr.net/npm/tiff.js@1.0.0/tiff.min.js";
	const MEMORY_SIZE = 16777216 * 5; // ~80MB allocation for tiff.js

	// --- COMPONENT STATE ---
	const _props = $props();
	const gradio = new Gradio<TiffEvents, TiffProps>(_props);

	// Derived State
	let value = $derived(gradio.props.value);
	// Use shared interactive state (handles input vs output context automatically)
	let interactive = $derived(gradio.shared.interactive ?? true);

	// Local state for the rendered pages
	let pages: string[] = $state([]);
	let page_index = $state(0);
	let uploading = $state(false);
	let lib_ready = $state(false);
	let processing = $state(false);
	let current_processed_url: string | null = $state(null);

	// --- LIFECYCLE & EFFECTS ---

	onMount(async () => {
		try {
			await loadScript(TIFF_LIB_URL);
			// Double check availability after loading
			if (window.Tiff) {
				window.Tiff.initialize({ TOTAL_MEMORY: MEMORY_SIZE });
				lib_ready = true;
			}
		} catch (e) {
			console.error("Failed to load Tiff.js backend:", e);
		}
	});

	// Reactive effect: Watch for value changes
	$effect(() => {
		// Reset if value is cleared
		if (!value) {
			pages = [];
			page_index = 0;
			current_processed_url = null;
			return;
		}

		// Process TIFF if it's a new file and library is ready
		// Note: When lib_ready becomes true, this effect re-runs.
		const file_url = value.url || value.path;
		if (lib_ready && file_url && file_url !== current_processed_url) {
			processTiff(value);
		}
	});

	function loadScript(src: string): Promise<void> {
		return new Promise((resolve, reject) => {
			// Case 1: Already fully loaded
			if (window.Tiff) return resolve();

			// Case 2: Script tag doesn't exist yet -> Create it
			if (!document.querySelector(`script[src="${src}"]`)) {
				const script = document.createElement("script");
				script.src = src;
				script.async = true;
				script.onload = () => resolve();
				script.onerror = () =>
					reject(new Error(`Failed to load script: ${src}`));
				document.head.appendChild(script);
				return;
			}

			// Case 3: Script tag exists, but window.Tiff is missing (race condition).
			// Poll until it's ready.
			const interval = setInterval(() => {
				if (window.Tiff) {
					clearInterval(interval);
					resolve();
				}
			}, 50);

			// Timeout after 5 seconds to avoid infinite loops
			setTimeout(() => {
				clearInterval(interval);
				if (!window.Tiff)
					reject(new Error("Timeout waiting for Tiff.js to load"));
			}, 5000);
		});
	}

	// --- CORE LOGIC (Client-Side Rendering) ---

	async function processTiff(file: FileData) {
		if (!lib_ready || !window.Tiff) return;

		const url = file.url || file.path;
		if (!url) return;

		processing = true;
		current_processed_url = url;

		let tiffInstance: TiffInstance | null = null;

		try {
			const response = await fetch(url);
			if (!response.ok)
				throw new Error(
					`Network response was not ok: ${response.status}`,
				);

			const buffer = await response.arrayBuffer();
			tiffInstance = new window.Tiff({ buffer });

			let totalPages = 1;
			try {
				totalPages = tiffInstance.countDirectory();
			} catch (e) {
				console.warn(
					"Could not read directory count, defaulting to 1 page.",
					e,
				);
			}

			const new_pages: string[] = [];

			for (let i = 0; i < totalPages; i++) {
				try {
					tiffInstance.setDirectory(i);
					const canvas = tiffInstance.toCanvas();
					if (canvas) {
						new_pages.push(canvas.toDataURL("image/png"));
					}
				} catch (e) {
					console.warn(`Skipped corrupted page ${i}`, e);
				}
			}

			pages = new_pages;
			page_index = 0;
		} catch (error) {
			console.error("TIFF processing failed:", error);
			gradio.dispatch("clear_status");
			// Allow retrying if processing failed
			current_processed_url = null;
		} finally {
			tiffInstance?.close();
			processing = false;
		}
	}

	// --- EVENT HANDLERS ---

	function handle_upload(event: CustomEvent<FileData | FileData[]>) {
		const file = Array.isArray(event.detail)
			? event.detail[0]
			: event.detail;
		if (!file) return;

		// Basic MIME-Type / Extension Check
		const name = (file.orig_name || file.path || "").toLowerCase();
		const is_tiff =
			name.endsWith(".tif") ||
			name.endsWith(".tiff") ||
			file.mime_type?.includes("tiff");

		if (!is_tiff) {
			console.warn("File rejected (not TIFF):", name, file.mime_type);
			gradio.dispatch("clear_status");
			return;
		}

		gradio.props.value = file;
		gradio.dispatch("upload");
		gradio.dispatch("change");
	}

	function handle_clear() {
		gradio.props.value = null;
		gradio.dispatch("clear");
		gradio.dispatch("change");
	}

	// SSR Safe Stream Mock
	const stream_handler = gradio.shared.client?.stream
		? gradio.shared.client.stream.bind(gradio.shared.client)
		: () => ({ close: () => {} }) as any;
</script>

<Block
	visible={gradio.shared.visible}
	elem_id={gradio.shared.elem_id}
	elem_classes={gradio.shared.elem_classes}
	allow_overflow={false}
>
	<BlockLabel
		show_label={gradio.shared.show_label}
		Icon={ImageIcon}
		label={gradio.shared.label || "TIFF Image"}
	/>

	{#if !value}
		{#if interactive}
			<div class="upload-wrapper">
				<Upload
					upload={gradio.shared.client.upload}
					{stream_handler}
					root={gradio.shared.root}
					bind:uploading
					filetype="image/tiff, .tif, .tiff"
					on:load={handle_upload}
				>
					<UploadText i18n={gradio.i18n} type="image" />
				</Upload>
			</div>
		{:else}
			<Empty size="large" unpadded_box={true}>
				<ImageIcon />
			</Empty>
		{/if}
	{:else}
		<div class="tiff-viewer">
			{#if interactive}
				<div class="action-buttons">
					<IconButtonWrapper>
						<IconButton
							Icon={Clear}
							label="Clear"
							on:click={handle_clear}
						/>
					</IconButtonWrapper>
				</div>
			{/if}

			<div class="image-wrapper" class:loading={processing}>
				{#if processing}
					<span class="loading-text">Rendering TIFF...</span>
				{:else if pages.length > 0}
					<img
						src={pages[page_index]}
						alt={`Page ${page_index + 1}`}
					/>
				{:else}
					<span class="error-text">Unable to render image</span>
				{/if}
			</div>

			<div class="controls-wrapper">
				{#if pages.length > 1}
					<div class="nav-controls">
						<button
							class="nav-btn"
							onclick={() => page_index > 0 && page_index--}
							disabled={page_index === 0}
							aria-label="Previous page"
						>
							←
						</button>
						<span class="page-count">
							Page {page_index + 1} / {pages.length}
						</span>
						<button
							class="nav-btn"
							onclick={() =>
								page_index < pages.length - 1 && page_index++}
							disabled={page_index === pages.length - 1}
							aria-label="Next page"
						>
							→
						</button>
					</div>
				{:else}
					<div></div>
				{/if}

				{#if gradio.props.show_download_button}
					<a
						href={value.url}
						download={value.orig_name || "image.tiff"}
						class="download-link"
						aria-label="Download Original"
					>
						<Download />
					</a>
				{/if}
			</div>
		</div>
	{/if}
</Block>

<style>
	.tiff-viewer {
		display: flex;
		flex-direction: column;
		width: 100%;
		position: relative;
		gap: 0.5rem;
	}

	.image-wrapper {
		position: relative;
		width: 100%;
		display: flex;
		justify-content: center;
		align-items: center;
		background-color: var(--background-fill-secondary);
		border-radius: var(--radius-lg);
		overflow: hidden;
		min-height: 200px;
		border: 1px solid var(--border-color-primary);
	}

	.image-wrapper.loading {
		opacity: 0.7;
	}

	.loading-text,
	.error-text {
		color: var(--body-text-color-subdued);
		font-family: var(--font-sans);
	}

	img {
		max-width: 100%;
		max-height: 70vh;
		object-fit: contain;
	}

	.controls-wrapper {
		display: flex;
		align-items: center;
		justify-content: space-between;
		width: 100%;
		gap: 0.5rem;
		min-height: 36px;
	}

	.nav-controls {
		display: flex;
		gap: 0.5rem;
		align-items: center;
		padding: 0.25rem 0.5rem;
		background: var(--background-fill-secondary);
		border-radius: var(--radius-md);
		border: 1px solid var(--border-color-primary);
		justify-content: center;
		margin: 0 auto;
	}

	.page-count {
		font-family: var(--font-mono);
		font-size: var(--text-sm);
		color: var(--body-text-color);
		min-width: 90px;
		text-align: center;
		user-select: none;
	}

	button.nav-btn {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 32px;
		height: 32px;
		border: 1px solid var(--border-color-primary);
		border-radius: var(--radius-sm);
		cursor: pointer;
		background: var(--background-fill-primary);
		color: var(--body-text-color);
		transition: all 0.2s;
	}

	button.nav-btn:hover:not(:disabled) {
		background: var(--background-fill-secondary);
	}

	button.nav-btn:disabled {
		opacity: 0.4;
		cursor: not-allowed;
	}

	.action-buttons {
		position: absolute;
		top: 8px;
		right: 8px;
		z-index: 10;
	}

	.download-link {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 36px;
		height: 36px;
		background: var(--background-fill-primary);
		border-radius: var(--radius-md);
		border: 1px solid var(--border-color-primary);
		color: var(--body-text-color);
		flex-shrink: 0;
	}

	.download-link:hover {
		background: var(--background-fill-secondary);
		color: var(--color-accent);
	}

	.download-link :global(svg) {
		width: 18px;
		height: 18px;
	}

	.upload-wrapper {
		height: 100%;
		min-height: 200px;
	}
</style>
