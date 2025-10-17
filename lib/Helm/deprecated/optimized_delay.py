# Alternative optimized delay implementation using numpy operations
def vectorized_process_chunk(self, chunk):
    """More efficient chunk processing using numpy vectorization"""
    chunk = chunk.astype(np.float32)
    
    # Process entire chunk at once instead of sample-by-sample
    output = np.copy(chunk)
    
    # Add delayed samples where available
    for i in range(len(chunk)):
        if i >= self.delay_samples:
            # Use samples from earlier in the same chunk
            delayed_sample = chunk[i - self.delay_samples]
        else:
            # Use samples from delay buffer
            buffer_idx = (self.delay_index - self.delay_samples + i) % self.delay_samples
            delayed_sample = self.delay_buffer[buffer_idx]
        
        output[i] += delayed_sample * self.volume_reduction
    
    # Update delay buffer with new chunk
    chunk_len = len(chunk)
    if chunk_len >= self.delay_samples:
        # Chunk is longer than delay buffer
        self.delay_buffer[:] = chunk[-self.delay_samples:]
        self.delay_index = 0
    else:
        # Update circular buffer
        end_idx = (self.delay_index + chunk_len) % self.delay_samples
        if end_idx > self.delay_index:
            self.delay_buffer[self.delay_index:end_idx] = chunk
        else:
            # Wrap around
            split = self.delay_samples - self.delay_index
            self.delay_buffer[self.delay_index:] = chunk[:split]
            self.delay_buffer[:end_idx] = chunk[split:]
        self.delay_index = end_idx
    
    # Normalize to prevent clipping
    max_val = np.max(np.abs(output))
    if max_val > 0.8:
        output *= (0.8 / max_val)
    
    return output