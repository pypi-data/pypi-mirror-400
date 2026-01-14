
export default {
    template: `
    <div ref="container" 
         style="position: relative; width: 100%; height: 100%; overflow: hidden;"
         @mousedown="onContainerMouseDown"
         @mousemove="onContainerMouseMove"
         @mouseup="onContainerMouseUp"
         @mouseleave="onContainerMouseLeave">
      
      <canvas 
        ref="canvas"
        tabindex="0"
        style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 0;"
      ></canvas>
      
      <div ref="nodesContainer" 
           class="graph-node"
           data-node-id="_root_"
           :data-x="panX"
           :data-y="panY"
           style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1;"
           :style="rootContainerStyle">
        <slot></slot>
      </div>
      <div style="position: absolute; top: 10px; right: 0px; background: rgba(0, 0, 0, 0.5); color: rgba(255, 255, 255, 0.5); padding: 8px; border-radius: 4px; font-size: 12px; pointer-events: none; z-index: 2;">
        HUD Info: <br>{{ panX.toFixed(0) }} <br> {{ panY.toFixed(0) }}
      </div>
    </div>
  `,
    props: {
        wires: Array
    },
    data() {
        return {
            ctx: null,
            nodes: new Map(),
            ports: new Map(),
            selectedNode: null,
            isDragging: false,
            isPanning: false,
            offsetX: 0,
            offsetY: 0,
            panX: 0,
            panY: 0,
            lastMouseX: 0,
            lastMouseY: 0,
            resizeObserver: null,
            mutationObserver: null
        };
    },
    computed: {
        rootContainerStyle() {
            return {
                transform: `translate(${this.panX}px, ${this.panY}px)`
            };
        }
    },
    mounted() {
        this.ctx = this.$refs.canvas.getContext('2d');
        this.resizeCanvas();

        this.resizeObserver = new ResizeObserver(() => {
            this.resizeCanvas();
        });
        this.resizeObserver.observe(this.$refs.container);

        // Watch for node changes in the DOM
        this.mutationObserver = new MutationObserver(() => {
            this.updateNodesAndPorts();
        });
        this.mutationObserver.observe(this.$refs.nodesContainer, {
            childList: true,
            subtree: true,
            attributes: true,
            attributeFilter: ['data-x', 'data-y', 'data-node-id', 'data-port-id', 'style']
        });

        this.updateNodesAndPorts();
        this.draw();

        this.$refs.canvas.focus();

        window.nodeGraphDebug = this;
    },
    beforeUnmount() {
        if (this.resizeObserver) {
            this.resizeObserver.disconnect();
        }
        if (this.mutationObserver) {
            this.mutationObserver.disconnect();
        }
    },
    watch: {
        wires: {
            handler() {
                this.draw();
            },
            deep: true
        },
        panX() {
            this.draw();
        },
        panY() {
            this.draw();
        }
    },
    methods: {
        resizeCanvas() {
            const canvas = this.$refs.canvas;
            const container = this.$refs.container;
            const rect = container.getBoundingClientRect();
            canvas.width = rect.width;
            canvas.height = rect.height;
            this.draw();
        },

        // Calculate absolute position by traversing parent chain (not)
        getAbsolutePosition(element) {
            let nc_coords = this.$refs.nodesContainer.getBoundingClientRect();
            let el_coords = element.getBoundingClientRect();

            let x = el_coords.x - nc_coords.x + this.panX;
            let y = el_coords.y - nc_coords.y + this.panY;
            // console.log(x, y);
            return { x, y };

            // let x = 0;
            // let y = 0;
            // let current = element;

            // while (current && current !== this.$refs.container) {
            //     if (current.hasAttribute('data-x') && current.hasAttribute('data-y')) {
            //         x += parseFloat(current.getAttribute('data-x')) || 0;
            //         y += parseFloat(current.getAttribute('data-y')) || 0;
            //         // x += parseFloat(current.offsetLeft) || 0;
            //         // y += parseFloat(current.offsetTop) || 0;
            //         // x += parseFloat(current.getAttribute('data-x'));
            //         // y += parseFloat(current.getAttribute('data-y'));
            //     }
            //     else { x += current.offsetLeft; y += current.offsetTop; }
            //     current = current.parentElement;
            // }
            // return { x, y };
        },

        // Get center point of an element in absolute graph coordinates
        getElementCenter(element) {
            const absolutePos = this.getAbsolutePosition(element);
            const width = element.offsetWidth;
            const height = element.offsetHeight;

            return {
                x: absolutePos.x + width / 2,
                y: absolutePos.y + height / 2
            };
        },

        updateNodesAndPorts() {
            this.nodes.clear();
            this.ports.clear();

            const nodeElements = this.$refs.nodesContainer.querySelectorAll('[data-node-id]');

            nodeElements.forEach(el => {
                const nodeId = el.getAttribute('data-node-id');
                if (nodeId === '_root_') return; // Skip root container

                const localX = parseFloat(el.getAttribute('data-x')) || 0;
                const localY = parseFloat(el.getAttribute('data-y')) || 0;
                const absolutePos = this.getAbsolutePosition(el);

                const width = el.offsetWidth;
                const height = el.offsetHeight;

                this.nodes.set(nodeId, {
                    id: nodeId,
                    localX: localX,
                    localY: localY,
                    absoluteX: absolutePos.x,
                    absoluteY: absolutePos.y,
                    element: el,
                    width: width,
                    height: height
                });

                // Find ports within this node
                const portElements = el.querySelectorAll('[data-port-id]');
                portElements.forEach(portEl => {

                    const portId = portEl.getAttribute('data-port-id');
                    const portKey = `${nodeId}:${portId}`;

                    // Get port center position relative to the graph
                    const portCenter = this.getElementCenter(portEl.querySelector(".node-port-center"));

                    this.ports.set(portKey, {
                        nodeId: nodeId,
                        portId: portId,
                        element: portEl,
                        x: portCenter.x,
                        y: portCenter.y
                    });
                });
            });

            this.draw();
        },

        draw() {
            const ctx = this.ctx;
            const canvas = this.$refs.canvas;
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            if (!this.wires || this.wires.length === 0) return;

            this.wires.forEach(wire => {
                const fromNode = this.nodes.get(wire.from_id);
                const toNode = this.nodes.get(wire.to_id);

                if (fromNode && toNode) {
                    // Determine start and end points (port or node center)
                    let fromPoint, toPoint;

                    if (wire.from_port) {
                        const portKey = `${wire.from_id}:${wire.from_port}`;
                        const port = this.ports.get(portKey);
                        if (port) {
                            fromPoint = { x: port.x, y: port.y };
                        } else {
                            // Fallback to node center if port not found
                            fromPoint = {
                                x: fromNode.absoluteX + fromNode.width / 2,
                                y: fromNode.absoluteY + fromNode.height / 2
                            };
                        }
                    } else {
                        fromPoint = {
                            x: fromNode.absoluteX + fromNode.width / 2,
                            y: fromNode.absoluteY + fromNode.height / 2
                        };
                    }

                    if (wire.to_port) {
                        const portKey = `${wire.to_id}:${wire.to_port}`;
                        const port = this.ports.get(portKey);
                        if (port) {
                            toPoint = { x: port.x, y: port.y };
                        } else {
                            // Fallback to node center if port not found
                            toPoint = {
                                x: toNode.absoluteX + toNode.width / 2,
                                y: toNode.absoluteY + toNode.height / 2
                            };
                        }
                    } else {
                        toPoint = {
                            x: toNode.absoluteX + toNode.width / 2,
                            y: toNode.absoluteY + toNode.height / 2
                        };
                    }

                    this.drawWire(fromPoint, toPoint, wire.style || 'straight', wire.from_color || '#4ecca3', wire.to_color || '#4ecca340');
                }
            });
        },

        drawWire(from, to, style, from_color, to_color) {
            const canvas = this.$refs.canvas;
            const ctx = this.ctx;

            var gw = Math.hypot(0, 0, from.x - to.x, from.y - to.y);
            var grd = ctx.createRadialGradient(from.x, from.y, 0, from.x, from.y, gw);

            // Debug gradient:
            // ctx.beginPath();
            // ctx.arc(from.x, from.y, 10, 0, 2 * Math.PI);
            // ctx.arc(from.x, from.y, gw, 0, 2 * Math.PI);
            // ctx.stroke();

            grd.addColorStop(.3, from_color);
            grd.addColorStop(.6, to_color);
            ctx.strokeStyle = grd;

            ctx.lineWidth = 1;
            ctx.beginPath();

            switch (style) {
                case 'straight':
                    ctx.moveTo(from.x, from.y);
                    ctx.lineTo(to.x, to.y);
                    break;

                case 'curved':
                    const midX = (from.x + to.x) / 2;
                    const midY = (from.y + to.y) / 2;
                    const dx = to.x - from.x;
                    const dy = to.y - from.y;
                    const offset = 50;
                    const controlX = midX - dy / Math.hypot(dx, dy) * offset;
                    const controlY = midY + dx / Math.hypot(dx, dy) * offset;

                    ctx.moveTo(from.x, from.y);
                    ctx.quadraticCurveTo(controlX, controlY, to.x, to.y);
                    break;

                case 'bezier':
                    const dist = Math.abs(to.x - from.x);
                    const controlOffset = Math.min(dist / 2, 200);

                    ctx.moveTo(from.x, from.y);
                    ctx.bezierCurveTo(
                        from.x + controlOffset, from.y,
                        to.x - controlOffset, to.y,
                        to.x, to.y
                    );
                    break;
            }

            ctx.stroke();
        },

        getNodeElementAtPoint(x, y) {
            const elements = document.elementsFromPoint(x, y);
            for (const el of elements) {
                if (el.hasAttribute('data-node-id') && el.getAttribute('data-node-id') !== '_root_') {
                    return el;
                }
            }
            return null;
        },

        onContainerMouseDown(e) {
            // Check if we clicked on a node
            const nodeElement = this.getNodeElementAtPoint(e.clientX, e.clientY);

            if (nodeElement) {
                // Dragging a node
                const nodeId = nodeElement.getAttribute('data-node-id');
                const node = this.nodes.get(nodeId);

                if (node) {
                    this.selectedNode = node;
                    this.isDragging = true;

                    // Calculate offset from the mouse to the node's local position
                    const parent = nodeElement.parentElement;
                    const parentRect = parent.getBoundingClientRect();
                    const mouseInParent = {
                        x: e.clientX - parentRect.left,
                        y: e.clientY - parentRect.top
                    };

                    this.offsetX = mouseInParent.x - node.localX;
                    this.offsetY = mouseInParent.y - node.localY;

                    this.$emit('node_clicked', { nodeId: node.id, shiftKey: e.shiftKey });
                }
            } else {
                // Dragging the background (pan)
                this.isPanning = true;
                this.lastMouseX = e.clientX;
                this.lastMouseY = e.clientY;
            }

            e.preventDefault();
        },

        onContainerMouseMove(e) {
            if (this.isDragging && this.selectedNode) {
                // Move the selected node
                const parent = this.selectedNode.element.parentElement;
                const parentRect = parent.getBoundingClientRect();

                // Calculate new position relative to parent
                const newX = e.clientX - parentRect.left - this.offsetX;
                const newY = e.clientY - parentRect.top - this.offsetY;

                this.selectedNode.localX = newX;
                this.selectedNode.localY = newY;
                this.selectedNode.element.setAttribute('data-x', newX);
                this.selectedNode.element.setAttribute('data-y', newY);
                this.selectedNode.element.style.transform = `translate(${newX}px, ${newY}px)`;

                this.$emit('node_moved', {
                    nodeId: this.selectedNode.id,
                    x: newX,
                    y: newY
                });

                // Update absolute positions and redraw
                this.updateNodesAndPorts();
            } else if (this.isPanning) {
                // Pan the entire graph
                const dx = e.clientX - this.lastMouseX;
                const dy = e.clientY - this.lastMouseY;

                this.panX += dx;
                this.panY += dy;

                this.lastMouseX = e.clientX;
                this.lastMouseY = e.clientY;

                // Update root container position
                this.$refs.nodesContainer.setAttribute('data-x', this.panX);
                this.$refs.nodesContainer.setAttribute('data-y', this.panY);

                this.updateNodesAndPorts();
            }
        },

        onContainerMouseUp() {
            this.isDragging = false;
            this.isPanning = false;
            this.selectedNode = null;
        },

        onContainerMouseLeave() {
            this.isDragging = false;
            this.isPanning = false;
            this.selectedNode = null;
        },

        getNodePositions(nodeIds) {
            const positions = {};

            // If no nodeIds provided, get all nodes
            const ids = nodeIds || Array.from(this.nodes.keys());

            ids.forEach(nodeId => {
                const el = this.$refs.nodesContainer.querySelector(`[data-node-id="${nodeId}"]`);
                if (el) {
                    // positions[nodeId] = {
                    //     x: parseFloat(el.getAttribute('data-x')) || 0,
                    //     y: parseFloat(el.getAttribute('data-y')) || 0
                    // };
                    positions[nodeId] = [
                        parseFloat(el.getAttribute('data-x')) || 0,
                        parseFloat(el.getAttribute('data-y')) || 0
                    ];
                }
            });

            return positions;
        },

        set_node_pos(nodeId, x, y) {
            const el = this.$refs.nodesContainer.querySelector(`[data-node-id="${nodeId}"]`);
            if (el) {
                el.setAttribute('data-x', x);
                el.setAttribute('data-y', y);
                el.style.transform = `translate(${x}px, ${y}px)`;

                // Trigger update to redraw wires
                this.updateNodesAndPorts();
            }
        },

        move_node(nodeId, dx, dy) {
            const el = this.$refs.nodesContainer.querySelector(`[data-node-id="${nodeId}"]`);
            if (el) {
                const currentX = parseFloat(el.getAttribute('data-x')) || 0;
                const currentY = parseFloat(el.getAttribute('data-y')) || 0;
                const newX = currentX + dx;
                const newY = currentY + dy;

                this.set_node_pos(nodeId, newX, newY);
                // el.setAttribute('data-x', newX);
                // el.setAttribute('data-y', newY);
                // el.style.transform = `translate(${newX}px, ${newY}px)`;

                // // Trigger update to redraw wires
                // this.updateNodesAndPorts();
            }
        },

        getNodesInRect(x, y, width, height) {
            const selRight = x + width;
            const selBottom = y + height;
            const selectedNodes = [];

            this.nodes.forEach((node, nodeId) => {
                const nodeLeft = node.absoluteX;
                const nodeTop = node.absoluteY;
                const nodeRight = nodeLeft + node.width;
                const nodeBottom = nodeTop + node.height;

                // Check intersection
                const intersects = !(
                    selRight < nodeLeft ||
                    x > nodeRight ||
                    selBottom < nodeTop ||
                    y > nodeBottom
                );

                if (intersects) {
                    selectedNodes.push({
                        id: nodeId,
                        x: node.absoluteX,
                        y: node.absoluteY,
                        width: node.width,
                        height: node.height
                    });
                }
            });

            return selectedNodes;
        }
    }
};