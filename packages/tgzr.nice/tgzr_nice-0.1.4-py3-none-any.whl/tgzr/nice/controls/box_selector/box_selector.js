export default {
    template: `
    <div ref="container" style="position: relative; width: 100%; height: 100%;">
      <!-- Canvas for drawing selection box -->
      <canvas 
        ref="canvas"
        @mousedown="onMouseDown"
        @mousemove="onMouseMove"
        @mouseup="onMouseUp"
        @mouseleave="onMouseLeave"
        style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 1000;"
      ></canvas>
      
      <!-- Children content -->
      <div ref="content" style="position: relative; width: 100%; height: 100%;">
        <slot></slot>
      </div>
    </div>
  `,

    data() {
        return {
            ctx: null,
            isSelecting: false,
            startX: 0,
            startY: 0,
            endX: 0,
            endY: 0,
            resizeObserver: null
        };
    },

    mounted() {
        this.ctx = this.$refs.canvas.getContext('2d');
        this.resizeCanvas();

        this.resizeObserver = new ResizeObserver(() => {
            this.resizeCanvas();
        });
        this.resizeObserver.observe(this.$refs.container);

        // Enable pointer events only when shift is pressed
        document.addEventListener('keydown', this.onKeyDown);
        document.addEventListener('keyup', this.onKeyUp);
    },

    beforeUnmount() {
        if (this.resizeObserver) {
            this.resizeObserver.disconnect();
        }
        document.removeEventListener('keydown', this.onKeyDown);
        document.removeEventListener('keyup', this.onKeyUp);
    },

    methods: {
        resizeCanvas() {
            const canvas = this.$refs.canvas;
            const container = this.$refs.container;
            const rect = container.getBoundingClientRect();
            canvas.width = rect.width;
            canvas.height = rect.height;
        },

        onKeyDown(e) {
            if (e.key === 'Shift') {
                this.$refs.canvas.style.pointerEvents = 'auto';
            }
        },

        onKeyUp(e) {
            if (e.key === 'Shift') {
                this.$refs.canvas.style.pointerEvents = 'none';
                // Cancel selection if in progress
                if (this.isSelecting) {
                    this.isSelecting = false;
                    this.clearCanvas();
                }
            }
        },

        getMousePos(e) {
            const rect = this.$refs.canvas.getBoundingClientRect();
            return {
                x: e.clientX - rect.left,
                y: e.clientY - rect.top
            };
        },

        onMouseDown(e) {
            // Only start if shift is pressed
            if (!e.shiftKey) return;

            const pos = this.getMousePos(e);
            this.isSelecting = true;
            this.startX = pos.x;
            this.startY = pos.y;
            this.endX = pos.x;
            this.endY = pos.y;

            e.preventDefault();
        },

        onMouseMove(e) {
            if (!this.isSelecting) return;

            const pos = this.getMousePos(e);
            this.endX = pos.x;
            this.endY = pos.y;

            this.drawSelectionBox();
        },

        onMouseUp(e) {
            if (!this.isSelecting) return;

            const x = Math.min(this.startX, this.endX);
            const y = Math.min(this.startY, this.endY);
            const width = Math.abs(this.endX - this.startX);
            const height = Math.abs(this.endY - this.startY);

            // Only emit if box has meaningful size
            if (width > 5 && height > 5) {
                this.$emit('box_selected', { x, y, width, height });
            }

            this.isSelecting = false;
            this.clearCanvas();
        },

        onMouseLeave(e) {
            if (this.isSelecting) {
                this.isSelecting = false;
                this.clearCanvas();
            }
        },

        clearCanvas() {
            const ctx = this.ctx;
            const canvas = this.$refs.canvas;
            ctx.clearRect(0, 0, canvas.width, canvas.height);
        },

        drawSelectionBox() {
            const ctx = this.ctx;
            const canvas = this.$refs.canvas;

            ctx.clearRect(0, 0, canvas.width, canvas.height);

            const x = Math.min(this.startX, this.endX);
            const y = Math.min(this.startY, this.endY);
            const width = Math.abs(this.endX - this.startX);
            const height = Math.abs(this.endY - this.startY);

            // Draw semi-transparent fill
            ctx.fillStyle = 'rgba(255, 255, 255, 0.1)';
            ctx.fillRect(x, y, width, height);

            // Draw border
            // ctx.strokeStyle = 'rgba(255, 255, 255, 0.5)';
            // ctx.lineWidth = 1;
            // ctx.strokeRect(x, y, width, height);
        }
    }
};