from fonadalabs import DenoiseStreamingClient

client = DenoiseStreamingClient(api_key="sk_ae283a1d3f602b7c96a3068260b42dc8a71a89624569fdf3")

# Callback for each denoised chunk
def on_chunk_ready(chunk):
    # Play or save the denoised chunk
    print(f"Received {len(chunk)} samples")

# Stream denoise a file
denoised = client.denoise_file_ws(
    file_path="test_audio.wav",
    output_path="clean_audio.wav",
    callback=on_chunk_ready
)

print("✅ Streaming complete!")
