/**
 * OBFUSCII Player Library with Debug Logging
 * Real LZMA decompression and .txv playback
 * MINIMAL MODIFICATION: Only theme-aware file loading added
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
        
        window.addEventListener('resize', () => this.adjustResponsiveSize());
        this.adjustResponsiveSize();
    }

    async initializeLZMA() {
        try {
            if (typeof LZMA === 'undefined') {
                console.log('🔍 LZMA not immediately available, waiting...');
                await this.waitForLZMA();
            }
            console.log('✅ LZMA library initialized successfully');
        } catch (error) {
            console.error('❌ LZMA initialization failed:', error);
            this.updatePlaybackInfo('LZMA library failed to load', 'error');
        }
    }

    waitForLZMA(timeout = 5000) {
        return new Promise((resolve, reject) => {
            const start = Date.now();
            const checkLZMA = () => {
                if (typeof LZMA !== 'undefined') {
                    console.log('✅ LZMA library loaded after', Date.now() - start, 'ms');
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
            console.log('🔍 Loading file:', file.name, file.size, 'bytes');
            this.updatePlaybackInfo('Loading .txv file...', 'loading');
            this.disableControls();
            
            const arrayBuffer = await file.arrayBuffer();
            console.log('🔍 File loaded as ArrayBuffer:', arrayBuffer.byteLength, 'bytes');
            
            const result = await this.parseTxvFile(arrayBuffer);
            
            this.frames = result.frames;
            this.fps = result.fps || 30;
            this.metadata = result.metadata;
            this.currentFrame = 0;
            
            console.log('✅ TXV parsing complete:', {
                frameCount: this.frames.length,
                fps: this.fps,
                firstFrameLength: this.frames[0] ? this.frames[0].length : 0,
                metadata: this.metadata
            });
            
            this.updateFileInfo(file.name, this.frames.length, this.fps);
            this.updatePlaybackInfo('Ready to play', 'ready');
            this.enableControls();
            
            // Auto-scale based on content size
            this.adjustResponsiveSize();
            
        } catch (error) {
            console.error('❌ File loading failed:', error);
            this.updatePlaybackInfo(`Error: ${error.message}`, 'error');
            this.disableControls();
        }
    }

    // THEME-AWARE TEST FILE LOADING - ONLY NEW ADDITION
    detectDarkMode() {
        if (document.documentElement.hasAttribute('data-theme')) {
            return document.documentElement.getAttribute('data-theme') === 'dark';
        }
        return window.matchMedia('(prefers-color-scheme: dark)').matches;
    }

    async loadTestFile() {
        try {
            this.updatePlaybackInfo('Loading demo file...', 'loading');
            this.disableControls();
            
            // Theme-aware file selection with fallback
            const isDarkMode = this.detectDarkMode();
            const filename = isDarkMode ? 'text_dark.txv' : 'test_light.txv';
            
            let response = await fetch(filename);
            
            // Fallback to test_light.txv if themed version doesn't exist
            if (!response.ok && filename !== 'test_light.txv') {
                console.log(`${filename} not found, falling back to test_light.txv`);
                response = await fetch('test_light.txv');
            }
            
            if (!response.ok) {
                throw new Error('Demo file not found');
            }
            
            const arrayBuffer = await response.arrayBuffer();
            const result = await this.parseTxvFile(arrayBuffer);
            
            this.frames = result.frames;
            this.fps = result.fps || 30;
            this.metadata = result.metadata;
            this.currentFrame = 0;
            
            console.log('✅ Demo file loaded:', {
                filename: filename,
                frameCount: this.frames.length,
                fps: this.fps
            });
            
            this.updateFileInfo(`Demo (${filename})`, this.frames.length, this.fps);
            this.updatePlaybackInfo('Ready to play', 'ready');
            this.enableControls();
            this.adjustResponsiveSize();
            
        } catch (error) {
            console.error('❌ Demo loading failed:', error);
            this.updatePlaybackInfo(`Error: ${error.message}`, 'error');
            this.disableControls();
        }
    }

    // ALL ORIGINAL METHODS BELOW - UNCHANGED
    async parseTxvFile(arrayBuffer) {
        try {
            console.log('🔍 Parsing TXV file:', arrayBuffer.byteLength, 'bytes');
            
            const view = new DataView(arrayBuffer);
            let offset = 0;

            // Read magic header
            const magic = new TextDecoder().decode(new Uint8Array(arrayBuffer, offset, 8));
            console.log('🔍 Magic header:', magic);
            
            if (magic !== 'OBFUSCII') {
                throw new Error(`Invalid magic header: ${magic}`);
            }
            offset += 8;

            // Read version
            const version = view.getUint32(offset, true);
            console.log('🔍 Version:', version);
            offset += 4;

            // Read metadata
            const metadataLength = view.getUint32(offset, true);
            console.log('🔍 Metadata length:', metadataLength);
            offset += 4;
            
            const metadataBytes = new Uint8Array(arrayBuffer, offset, metadataLength);
            const metadataJson = new TextDecoder().decode(metadataBytes);
            const metadata = JSON.parse(metadataJson);
            console.log('🔍 Metadata:', metadata);
            offset += metadataLength;

            // Read frame count
            const frameCount = view.getUint32(offset, true);
            console.log('🔍 Frame count:', frameCount);
            offset += 4;

            const frames = [];
            
            // Progress tracking
            console.log('🔍 Starting frame decompression...');
            
            // Read each frame
            for (let i = 0; i < frameCount; i++) {
                const frameIndex = view.getUint32(offset, true);
                offset += 4;
                
                const compressedLength = view.getUint32(offset, true);
                offset += 4;
                
                const compressedData = new Uint8Array(arrayBuffer, offset, compressedLength);
                offset += compressedLength;
                
                if (i === 0) {
                    console.log('🔍 First frame details:', {
                        frameIndex,
                        compressedLength,
                        compressedDataSample: Array.from(compressedData.slice(0, 20))
                    });
                }
                
                try {
                    const decompressedFrame = await this.decompressFrame(compressedData, metadata.width, metadata.height, i);
                    frames.push(decompressedFrame);
                } catch (frameError) {
                    console.error(`❌ Frame ${i} failed:`, frameError);
                    const fallbackFrame = this.createFallbackFrame(metadata.width, metadata.height, i);
                    frames.push(fallbackFrame);
                }
                
                // Progress update
                if (i % 10 === 0) {
                    this.updatePlaybackInfo(`Loading frame ${i}/${frameCount}...`, 'loading');
                }
            }

            console.log('✅ All frames loaded:', frames.length);
            
            return {
                frames: frames,
                fps: metadata.fps,
                width: metadata.width,
                height: metadata.height,
                metadata: metadata
            };
            
        } catch (error) {
            console.error('❌ TXV parsing failed:', error);
            throw new Error(`TXV parsing failed: ${error.message}`);
        }
    }

    async decompressFrame(compressedData, width, height, frameIndex) {
        try {
            console.log(`🔍 Decompressing frame ${frameIndex}:`, {
                compressedDataLength: compressedData.length,
                width,
                height,
                expectedCharacters: width * height
            });
            
            // LZMA decompression with detailed logging
            const rleSegments = await this.decompressLZMA(compressedData, frameIndex);
            
            // Reconstruct ASCII frame from RLE segments
            let frameString = '';
            let position = 0;
            
            if (frameIndex === 0) {
                console.log('🔍 First frame RLE reconstruction:', {
                    segmentCount: rleSegments.length,
                    firstSegments: rleSegments.slice(0, 5),
                    lastSegments: rleSegments.slice(-5)
                });
            }
            
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
            
            if (frameIndex === 0) {
                console.log('✅ First frame reconstructed:', {
                    finalLength: frameString.length,
                    expectedLength: width * height + height - 1, // +newlines -last newline
                    hasNewlines: frameString.includes('\n'),
                    lineCount: frameString.split('\n').length,
                    expectedLines: height,
                    firstLine: frameString.split('\n')[0],
                    firstLineLength: frameString.split('\n')[0].length,
                    expectedLineLength: width
                });
            }
            
            return frameString;
            
        } catch (error) {
            console.error(`❌ Frame ${frameIndex} decompression failed:`, error);
            return this.createFallbackFrame(width, height, frameIndex);
        }
    }

    async decompressLZMA(compressedData, frameIndex) {
        return new Promise((resolve, reject) => {
            try {
                if (typeof LZMA === 'undefined') {
                    throw new Error('LZMA library not available');
                }
                
                const dataArray = Array.from(compressedData);
                
                if (frameIndex === 0) {
                    console.log('🔍 LZMA.decompress input:', {
                        dataArrayLength: dataArray.length,
                        firstElements: dataArray.slice(0, 10),
                        lastElements: dataArray.slice(-10)
                    });
                }
                
                LZMA.decompress(dataArray, (result, error) => {
                    if (frameIndex === 0) {
                        console.log('🔍 LZMA.decompress callback:', {
                            hasError: !!error,
                            error: error,
                            resultType: typeof result,
                            resultLength: result ? result.length : 0,
                            resultIsArray: Array.isArray(result),
                            resultConstructor: result ? result.constructor.name : 'none'
                        });
                    }
                    
                    if (error) {
                        reject(new Error(`LZMA decompression failed: ${error}`));
                        return;
                    }
                    
                    if (!result) {
                        reject(new Error('LZMA returned null result'));
                        return;
                    }
                    
                    try {
                        // Convert LZMA result to string
                        let decompressedString;
                        if (typeof result === 'string') {
                            decompressedString = result;
                        } else if (Array.isArray(result)) {
                            decompressedString = new TextDecoder().decode(new Uint8Array(result));
                        } else {
                            throw new Error(`Unexpected LZMA result type: ${typeof result}`);
                        }
                        
                        if (frameIndex === 0) {
                            console.log('🔍 LZMA decompressed string:', {
                                length: decompressedString.length,
                                firstChars: decompressedString.slice(0, 50),
                                containsNewlines: decompressedString.includes('\n')
                            });
                        }
                        
                        // Parse RLE segments from decompressed string
                        const rleSegments = this.parseRLESegments(decompressedString);
                        
                        if (frameIndex === 0) {
                            console.log('✅ RLE segments parsed:', {
                                segmentCount: rleSegments.length,
                                firstSegments: rleSegments.slice(0, 5)
                            });
                        }
                        
                        resolve(rleSegments);
                        
                    } catch (parseError) {
                        reject(new Error(`RLE parsing failed: ${parseError.message}`));
                    }
                });
                
            } catch (error) {
                reject(error);
            }
        });
    }

    parseRLESegments(rleString) {
        const segments = [];
        const lines = rleString.trim().split('\n');
        
        for (const line of lines) {
            if (!line.trim()) continue;
            
            try {
                const [char, countStr] = line.split(':');
                const count = parseInt(countStr, 10);
                
                if (isNaN(count) || count <= 0) {
                    console.warn('Invalid RLE segment:', line);
                    continue;
                }
                
                // Handle special characters
                let actualChar = char;
                if (char === '\\n') actualChar = '\n';
                else if (char === '\\t') actualChar = '\t';
                else if (char === '\\\\') actualChar = '\\';
                
                segments.push([actualChar, count]);
                
            } catch (error) {
                console.warn('Failed to parse RLE segment:', line, error);
            }
        }
        
        return segments;
    }

    createFallbackFrame(width, height, frameIndex) {
        console.log(`🔧 Creating fallback frame ${frameIndex} (${width}x${height})`);
        
        // Create a simple pattern based on frame index
        const chars = ' .:-=+*#%@';
        let frame = '';
        
        for (let y = 0; y < height; y++) {
            for (let x = 0; x < width; x++) {
                const charIndex = (x + y + frameIndex) % chars.length;
                frame += chars[charIndex];
            }
            if (y < height - 1) frame += '\n';
        }
        
        return frame;
    }

    play() {
        if (this.frames.length === 0) {
            this.updatePlaybackInfo('No frames to play', 'error');
            return;
        }
        
        this.isPlaying = true;
        this.lastFrameTime = performance.now();
        this.updatePlaybackInfo('Playing...', 'playing');
        this.animate();
        
        console.log('▶️ Playback started');
    }

    pause() {
        this.isPlaying = false;
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
            this.animationId = null;
        }
        this.updatePlaybackInfo('Paused', 'paused');
        console.log('⏸️ Playback paused');
    }

    stop() {
        this.isPlaying = false;
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
            this.animationId = null;
        }
        this.currentFrame = 0;
        if (this.frames.length > 0) {
            this.displayFrame(0);
        }
        this.updatePlaybackInfo('Stopped', 'stopped');
        console.log('⏹️ Playback stopped');
    }

    animate() {
        if (!this.isPlaying) return;

        const now = performance.now();
        const frameInterval = 1000 / this.fps;

        if (now - this.lastFrameTime >= frameInterval) {
            this.displayFrame(this.currentFrame);
            this.currentFrame = (this.currentFrame + 1) % this.frames.length;
            this.lastFrameTime = now;
            
            // Update playback info with current frame
            this.updatePlaybackInfo(`Playing frame ${this.currentFrame + 1}/${this.frames.length}`, 'playing');
        }

        this.animationId = requestAnimationFrame(() => this.animate());
    }

    displayFrame(frameIndex) {
        if (frameIndex < this.frames.length) {
            this.asciiContent.textContent = this.frames[frameIndex];
        }
    }

    updateScale(scale) {
        const percentage = Math.round(scale * 100);
        this.scaleValue.textContent = `${percentage}%`;
        
        const fontSize = 6 * scale;
        this.asciiContent.style.fontSize = `${fontSize}px`;
        
        console.log('🔧 Scale updated:', `${percentage}%`);
    }

    adjustResponsiveSize() {
        // Auto-adjust font size based on container size and content
        const container = this.asciiContent.parentElement;
        const containerWidth = container.clientWidth;
        const containerHeight = container.clientHeight;
        
        if (this.metadata && containerWidth && containerHeight) {
            const scaleX = containerWidth / (this.metadata.width * 7); // ~7px per char
            const scaleY = containerHeight / (this.metadata.height * 7); // ~7px per line
            const optimalScale = Math.min(scaleX, scaleY, 3); // Cap at 3x
            
            if (optimalScale > 0.1) {
                this.scaleSlider.value = optimalScale;
                this.updateScale(optimalScale);
            }
        }
    }

    updateFileInfo(filename, frameCount, fps) {
        const duration = frameCount / fps;
        this.fileInfo.textContent = `${filename} • ${frameCount} frames • ${fps} FPS • ${duration.toFixed(1)}s`;
    }

    updatePlaybackInfo(message, status = '') {
        this.playbackInfo.textContent = message;
        this.playbackInfo.className = `playback-info ${status}`;
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
}

// Initialize player when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.player = new OBFUSCIIPlayer();
    console.log('🎬 OBFUSCII Player initialized');
});