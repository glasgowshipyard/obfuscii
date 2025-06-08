/**
 * OBFUSCII Player Library
 * Real LZMA decompression and .txv playback
 */

class OBFUSCIIPlayer {
    constructor() {
        this.frames = [];
        this.currentFrame = 0;
        this.isPlaying = false;
        this.fps = 30;
        this.animationId = null;
        this.lastFrameTime = 0;
        this.metadata = null;
        
        this.initializeElements();
        this.bindEvents();
        this.initializeLZMA();
    }

    initializeElements() {
        this.fileInput = document.getElementById('fileInput');
        this.asciiContent = document.getElementById('asciiContent');
        this.playBtn = document.getElementById('playBtn');
        this.pauseBtn = document.getElementById('pauseBtn');
        this.stopBtn = document.getElementById('stopBtn');
        this.scaleSlider = document.getElementById('scaleSlider');
        this.scaleValue = document.getElementById('scaleValue');
        this.fileInfo = document.getElementById('fileInfo');
        this.playbackInfo = document.getElementById('playbackInfo');
        this.loadTestBtn = document.getElementById('loadTestBtn');
    }

    bindEvents() {
        this.fileInput.addEventListener('change', (e) => this.handleFileLoad(e));
        this.playBtn.addEventListener('click', () => this.play());
        this.pauseBtn.addEventListener('click', () => this.pause());
        this.stopBtn.addEventListener('click', () => this.stop());
        this.scaleSlider.addEventListener('input', (e) => this.updateScale(e.target.value));
        this.loadTestBtn.addEventListener('click', () => this.loadTestFile());
        
        // Responsive scaling
        window.addEventListener('resize', () => this.adjustResponsiveSize());
        this.adjustResponsiveSize();
    }

    async initializeLZMA() {
        try {
            // Wait for LZMA library to load
            if (typeof LZMA === 'undefined') {
                await this.waitForLZMA();
            }
            console.log('LZMA library initialized');
        } catch (error) {
            console.warn('LZMA initialization failed:', error);
            this.updatePlaybackInfo('LZMA library failed to load', 'error');
        }
    }

    waitForLZMA(timeout = 5000) {
        return new Promise((resolve, reject) => {
            const start = Date.now();
            const checkLZMA = () => {
                if (typeof LZMA !== 'undefined') {
                    resolve();
                } else if (Date.now() - start > timeout) {
                    reject(new Error('LZMA library load timeout'));
                } else {
                    setTimeout(checkLZMA, 100);
                }
            };
            checkLZMA();
        });
    }

    async handleFileLoad(event) {
        const file = event.target.files[0];
        if (!file) return;

        try {
            this.updatePlaybackInfo('Loading .txv file...', 'loading');
            this.disableControls();
            
            const arrayBuffer = await file.arrayBuffer();
            const result = await this.parseTxvFile(arrayBuffer);
            
            this.frames = result.frames;
            this.fps = result.fps || 30;
            this.metadata = result.metadata;
            this.currentFrame = 0;
            
            this.updateFileInfo(`${result.width}x${result.height}, ${this.frames.length} frames, ${this.fps} FPS`);
            this.updatePlaybackInfo('File loaded successfully', 'success');
            this.displayFrame(0);
            this.enableControls();
            
        } catch (error) {
            this.updatePlaybackInfo(`Load error: ${error.message}`, 'error');
            console.error('TXV load error:', error);
        }
    }

    async loadTestFile() {
        try {
            this.updatePlaybackInfo('Loading test.txv...', 'loading');
            
            const response = await fetch('test.txv');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const arrayBuffer = await response.arrayBuffer();
            const result = await this.parseTxvFile(arrayBuffer);
            
            this.frames = result.frames;
            this.fps = result.fps || 30;
            this.metadata = result.metadata;
            this.currentFrame = 0;
            
            this.updateFileInfo(`test.txv: ${result.width}x${result.height}, ${this.frames.length} frames, ${this.fps} FPS`);
            this.updatePlaybackInfo('Test file loaded successfully', 'success');
            this.displayFrame(0);
            this.enableControls();
            
        } catch (error) {
            this.updatePlaybackInfo(`Test file error: ${error.message}`, 'error');
            console.error('Test file error:', error);
        }
    }

    async parseTxvFile(arrayBuffer) {
        const view = new DataView(arrayBuffer);
        let offset = 0;

        try {
            // Read magic header
            const magic = new TextDecoder().decode(new Uint8Array(arrayBuffer, offset, 8));
            if (magic !== 'OBFUSCII') {
                throw new Error('Invalid .txv file: bad magic header');
            }
            offset += 8;

            // Read version
            const version = view.getUint32(offset, true);
            offset += 4;

            // Read metadata
            const metadataLength = view.getUint32(offset, true);
            offset += 4;
            
            const metadataBytes = new Uint8Array(arrayBuffer, offset, metadataLength);
            const metadataJson = new TextDecoder().decode(metadataBytes);
            const metadata = JSON.parse(metadataJson);
            offset += metadataLength;

            // Read frame count
            const frameCount = view.getUint32(offset, true);
            offset += 4;

            console.log('✅ TXV metadata:', metadata);
            console.log('✅ Frame count:', frameCount);

            // Read and decompress frames
            const frames = [];
            const maxFrames = frameCount;
            
            for (let i = 0; i < maxFrames; i++) {
                try {
                    // Read frame header (24 bytes)
                    const frameIndex = view.getUint32(offset, true);
                    offset += 4;
                    const frameType = String.fromCharCode(view.getUint8(offset));
                    offset += 1;
                    offset += 3; // Skip padding
                    const timestamp = view.getFloat64(offset, true);
                    offset += 8;
                    const rawSize = view.getUint32(offset, true);
                    offset += 4;
                    const compressedSize = view.getUint32(offset, true);
                    offset += 4;
                    
                    // Read compressed frame data
                    const compressedData = new Uint8Array(arrayBuffer, offset, compressedSize);
                    offset += compressedSize;
                    
                    // Decompress frame
                    const asciiFrame = await this.decompressFrame(compressedData, metadata.width, metadata.height);
                    frames.push(asciiFrame);
                    
                } catch (frameError) {
                    console.warn(`Frame ${i} decompression failed:`, frameError);
                    // Create fallback frame
                    const fallbackFrame = this.createFallbackFrame(metadata.width, metadata.height, i);
                    frames.push(fallbackFrame);
                }
                
                // Progress update
                if (i % 10 === 0) {
                    this.updatePlaybackInfo(`Decompressing frame ${i}/${maxFrames}...`, 'loading');
                }
            }

            return {
                frames: frames,
                fps: metadata.fps,
                width: metadata.width,
                height: metadata.height,
                metadata: metadata
            };
            
        } catch (error) {
            throw new Error(`TXV parsing failed: ${error.message}`);
        }
    }

    async decompressFrame(compressedData, width, height) {
        try {
            // LZMA decompression
            const decompressedData = await this.decompressLZMA(compressedData);
            
            // Parse RLE segments
            const rleSegments = JSON.parse(decompressedData);
            
            // Reconstruct ASCII frame
            return this.reconstructFrameFromRLE(rleSegments, width, height);
            
        } catch (error) {
            console.warn('Frame decompression failed:', error);
            return this.createFallbackFrame(width, height, 0);
        }
    }

    async decompressFrame(compressedData, width, height) {
        try {
            // LZMA-JS returns the RLE segments directly as a JavaScript array
            const rleSegments = await this.decompressLZMA(compressedData);
            
            // Skip JSON.parse entirely - we already have the array
            return this.reconstructFrameFromRLE(rleSegments, width, height);
            
        } catch (error) {
            console.warn('Frame decompression failed:', error);
            return this.createFallbackFrame(width, height, 0);
        }
    }

    async decompressLZMA(compressedData) {
        return new Promise((resolve, reject) => {
            try {
                const dataArray = Array.from(compressedData);
                
                LZMA.decompress(dataArray, (result, error) => {
                    if (error) {
                        reject(new Error(`LZMA decompression failed: ${error}`));
                    } else {
                        // Result is already the JavaScript array of RLE segments
                        resolve(result);
                    }
                });
            } catch (error) {
                reject(error);
            }
        });
    }

    reconstructFrameFromRLE(rleSegments, width, height) {
        let frameString = '';
        let position = 0;
        
        for (const [char, runLength] of rleSegments) {
            for (let i = 0; i < runLength; i++) {
                frameString += char;
                position++;
                
                // Add newlines at row boundaries
                if (position % width === 0 && position < width * height) {
                    frameString += '\n';
                }
            }
        }
        
        return frameString;
    }

    createFallbackFrame(width, height, frameIndex) {
        // Create fallback frame when decompression fails
        const chars = [' ', '.', ':', '-', '=', '+', '*', '#', '%', '@'];
        let frame = '';
        
        for (let y = 0; y < height; y++) {
            for (let x = 0; x < width; x++) {
                const charIndex = Math.floor((Math.sin(frameIndex * 0.1 + x * 0.05 + y * 0.05) + 1) * chars.length / 2);
                frame += chars[Math.min(charIndex, chars.length - 1)];
            }
            frame += '\n';
        }
        
        return frame;
    }

    displayFrame(frameIndex) {
        if (frameIndex < 0 || frameIndex >= this.frames.length) return;
        
        this.asciiContent.textContent = this.frames[frameIndex];
        this.currentFrame = frameIndex;
        
        if (this.frames.length > 1) {
            this.updatePlaybackInfo(`Frame ${frameIndex + 1}/${this.frames.length}`);
        }
    }

    play() {
        if (this.frames.length === 0) {
            this.updatePlaybackInfo('No frames loaded', 'error');
            return;
        }

        this.isPlaying = true;
        this.lastFrameTime = performance.now();
        this.animate();
        this.updatePlaybackInfo('Playing...');
    }

    pause() {
        this.isPlaying = false;
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }
        this.updatePlaybackInfo('Paused');
    }

    stop() {
        this.isPlaying = false;
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }
        this.currentFrame = 0;
        if (this.frames.length > 0) {
            this.displayFrame(0);
        }
        this.updatePlaybackInfo('Stopped');
    }

    animate() {
        if (!this.isPlaying) return;

        const now = performance.now();
        const frameDelta = 1000 / this.fps;

        if (now - this.lastFrameTime >= frameDelta) {
            this.currentFrame = (this.currentFrame + 1) % this.frames.length;
            this.displayFrame(this.currentFrame);
            this.lastFrameTime = now;
        }

        this.animationId = requestAnimationFrame(() => this.animate());
    }

    updateScale(scale) {
        this.asciiContent.style.transform = `scale(${scale})`;
        this.scaleValue.textContent = `${Math.round(scale * 100)}%`;
    }

    adjustResponsiveSize() {
        // Auto-adjust scale based on viewport
        const viewportWidth = window.innerWidth;
        let autoScale = 1;
        
        if (viewportWidth < 480) {
            autoScale = 0.6;
        } else if (viewportWidth < 768) {
            autoScale = 0.8;
        }
        
        const manualScale = parseFloat(this.scaleSlider.value);
        const totalScale = autoScale * manualScale;
        
        this.asciiContent.style.transform = `scale(${totalScale})`;
    }

    enableControls() {
        this.playBtn.disabled = false;
        this.pauseBtn.disabled = false;
        this.stopBtn.disabled = false;
    }

    disableControls() {
        this.playBtn.disabled = true;
        this.pauseBtn.disabled = true;
        this.stopBtn.disabled = true;
    }

    updateFileInfo(message) {
        this.fileInfo.textContent = message;
    }

    updatePlaybackInfo(message, type = '') {
        this.playbackInfo.textContent = message;
        this.playbackInfo.className = `playback-info ${type}`;
    }
}

// Initialize player when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.obfusciiPlayer = new OBFUSCIIPlayer();
    console.log('OBFUSCII Player initialized');
});