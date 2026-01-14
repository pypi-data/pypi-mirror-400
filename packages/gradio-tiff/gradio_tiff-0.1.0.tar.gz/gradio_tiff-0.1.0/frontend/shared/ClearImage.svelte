<script lang="ts">
	import { IconButton, IconButtonWrapper } from "@gradio/atoms";
	import { Clear } from "@gradio/icons";

	let { onremove_image } = $props();
</script>

<IconButtonWrapper>
	<IconButton
		Icon={Clear}
		label="Remove Image"
		on:click={(event) => {
			if (onremove_image) onremove_image();
			event.stopPropagation();
		}}
	/>
</IconButtonWrapper>
