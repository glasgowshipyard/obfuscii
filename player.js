/**
 * OBFUSCII Player Library with Debug Logging
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
                firstFrameLength: this.frames[0] ? this.frames[0].length : 0
            });
            
            this.updateFileInfo(`${result.width}x${result.height}, ${this.frames.length} frames, ${this.fps} FPS`);
            this.updatePlaybackInfo('File loaded successfully', 'success');
            this.displayFrame(0);
            this.enableControls();
            
        } catch (error) {
            console.error('❌ File load error:', error);
            this.updatePlaybackInfo(`Load error: ${error.message}`, 'error');
        }
    }

    async loadTestFile() {
        try {
            console.log('🔍 Loading test.txv...');
            this.updatePlaybackInfo('Loading test.txv...', 'loading');
            
            const response = await fetch('test.txv');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const arrayBuffer = await response.arrayBuffer();
            console.log('🔍 test.txv loaded:', arrayBuffer.byteLength, 'bytes');
            
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
            console.error('❌ Test file error:', error);
            this.updatePlaybackInfo(`Test file error: ${error.message}`, 'error');
        }
    }

    async parseTxvFile(arrayBuffer) {
        const view = new DataView(arrayBuffer);
        let offset = 0;

        try {
            console.log('🔍 Parsing TXV file structure...');
            
            // Read magic header
            const magic = new TextDecoder().decode(new Uint8Array(arrayBuffer, offset, 8));
            console.log('🔍 Magic header:', magic);
            if (magic !== 'OBFUSCII') {
                throw new Error('Invalid .txv file: bad magic header');
            }
            offset += 8;

            // Read version
            const version = view.getUint32(offset, true);
            console.log('🔍 TXV version:', version);
            offset += 4;

            // Read metadata
            const metadataLength = view.getUint32(offset, true);
            offset += 4;
            console.log('🔍 Metadata length:', metadataLength, 'bytes');
            
            const metadataBytes = new Uint8Array(arrayBuffer, offset, metadataLength);
            const metadataJson = new TextDecoder().decode(metadataBytes);
            const metadata = JSON.parse(metadataJson);
            offset += metadataLength;

            console.log('✅ TXV metadata:', metadata);

            // Read frame count
            const frameCount = view.getUint32(offset, true);
            offset += 4;
            console.log('✅ Frame count:', frameCount);

            // Load ALL frames with detailed logging
            const frames = [];
            
            for (let i = 0; i < frameCount; i++) {
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
                    
                    if (i === 0 || i % 10 === 0) {
                        console.log(`🔍 Frame ${i} header:`, {
                            frameIndex, frameType, timestamp, rawSize, compressedSize
                        });
                    }
                    
                    // Read compressed frame data
                    const compressedData = new Uint8Array(arrayBuffer, offset, compressedSize);
                    offset += compressedSize;
                    
                    if (i === 0) {
                        console.log('🔍 First frame compressed data:', {
                            length: compressedData.length,
                            firstBytes: Array.from(compressedData.slice(0, 10)),
                            lastBytes: Array.from(compressedData.slice(-10))
                        });
                    }
                    
                    // Decompress frame with detailed logging
                    const asciiFrame = await this.decompressFrame(compressedData, metadata.width, metadata.height, i);
                    frames.push(asciiFrame);
                    
                    if (i === 0) {
                        console.log('🔍 First frame decompressed:', {
                            type: typeof asciiFrame,
                            length: asciiFrame.length,
                            hasNewlines: asciiFrame.includes('\n'),
                            lineCount: asciiFrame.split('\n').length,
                            firstLine: asciiFrame.split('\n')[0],
                            preview: asciiFrame.substring(0, 100)
                        });
                    }
                    
                } catch (frameError) {
                    console.warn(`❌ Frame ${i} decompression failed:`, frameError);
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
                            resultConstructor: result ? result.constructor.name : null
                        });
                    }
                    
                    if (error) {
                        reject(new Error(`LZMA decompression failed: ${error}`));
                    } else {
                        try {
                            // Handle different return types from LZMA.decompress
                            let jsonString;
                            if (typeof result === 'string') {
                                jsonString = result;
                                if (frameIndex === 0) {
                                    console.log('🔍 LZMA returned string directly');
                                }
                            } else if (Array.isArray(result)) {
                                // Convert array of bytes to string
                                jsonString = new TextDecoder().decode(new Uint8Array(result));
                                if (frameIndex === 0) {
                                    console.log('🔍 LZMA returned array, converted to string');
                                }
                            } else {
                                // Try to decode as Uint8Array
                                jsonString = new TextDecoder().decode(new Uint8Array(result));
                                if (frameIndex === 0) {
                                    console.log('🔍 LZMA returned unknown type, attempting decode');
                                }
                            }
                            
                            if (frameIndex === 0) {
                                console.log('🔍 JSON string to parse:', {
                                    length: jsonString.length,
                                    preview: jsonString.substring(0, 200),
                                    hasValidJson: jsonString.startsWith('[')
                                });
                            }
                            
                            const rleSegments = JSON.parse(jsonString);
                            
                            if (frameIndex === 0) {
                                console.log('✅ RLE segments parsed:', {
                                    segmentCount: rleSegments.length,
                                    firstSegment: rleSegments[0],
                                    lastSegment: rleSegments[rleSegments.length - 1],
                                    totalCharacters: rleSegments.reduce((sum, [char, count]) => sum + count, 0)
                                });
                            }
                            
                            resolve(rleSegments);
                        } catch (parseError) {
                            console.error('❌ JSON parsing failed:', parseError);
                            reject(new Error(`JSON parsing failed: ${parseError.message}`));
                        }
                    }
                });
                
            } catch (error) {
                console.error('❌ LZMA setup failed:', error);
                reject(error);
            }
        });
    }

    createFallbackFrame(width, height, frameIndex) {
        console.log(`⚠️ Creating fallback frame ${frameIndex}`);
        // Create fallback frame when decompression fails
        const chars = [' ', '.', ':', '-', '=', '+', '*', '#', '%', '@'];
        let frame = '';
        
        for (let y = 0; y < height; y++) {
            for (let x = 0; x < width; x++) {
                const charIndex = Math.floor((Math.sin(frameIndex * 0.1 + x * 0.05 + y * 0.05) + 1) * chars.length / 2);
                frame += chars[Math.min(charIndex, chars.length - 1)];
            }
            if (y < height - 1) frame += '\n';
        }
        
        return frame;
    }

    displayFrame(frameIndex) {
        if (frameIndex < 0 || frameIndex >= this.frames.length) {
            console.warn('⚠️ Invalid frame index:', frameIndex, 'of', this.frames.length);
            return;
        }
        
        const frameContent = this.frames[frameIndex];
        
        // Debug the content being displayed
        if (frameIndex === 0) {
            console.log('🔍 Displaying first frame:', {
                frameIndex,
                contentType: typeof frameContent,
                contentLength: frameContent.length,
                hasNewlines: frameContent.includes('\n'),
                lineCount: frameContent.split('\n').length,
                firstLine: frameContent.split('\n')[0],
                firstLineLength: frameContent.split('\n')[0].length,
                preview: frameContent.substring(0, 100)
            });
        }
        
        // Set the content using textContent (should preserve newlines with <pre> tag)
        this.asciiContent.textContent = frameContent;
        this.currentFrame = frameIndex;
        
        if (this.frames.length > 1) {
            this.updatePlaybackInfo(`Frame ${frameIndex + 1}/${this.frames.length}`);
        }
        
        // Debug what's actually in the DOM
        if (frameIndex === 0) {
            console.log('🔍 DOM after setting textContent:', {
                elementTagName: this.asciiContent.tagName,
                elementTextContent: this.asciiContent.textContent.substring(0, 100),
                elementInnerHTML: this.asciiContent.innerHTML.substring(0, 100),
                elementComputedStyle: window.getComputedStyle(this.asciiContent).whiteSpace
            });
        }
    }

    play() {
        if (this.frames.length === 0) {
            this.updatePlaybackInfo('No frames loaded', 'error');
            return;
        }

        console.log('▶️ Starting playback');
        this.isPlaying = true;
        this.lastFrameTime = performance.now();
        this.animate();
        this.updatePlaybackInfo('Playing...');
    }

    pause() {
        console.log('⏸️ Pausing playback');
        this.isPlaying = false;
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }
        this.updatePlaybackInfo('Paused');
    }

    stop() {
        console.log('⏹️ Stopping playback');
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
    console.log('✅ OBFUSCII Player initialized with debugging');
});