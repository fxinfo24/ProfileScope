import React, { useEffect, useRef, useState } from 'react';

interface Node {
    id: string;
    group: number;
    radius: number;
    x?: number;
    y?: number;
    vx?: number;
    vy?: number;
}

interface Link {
    source: string | Node;
    target: string | Node;
    value: number;
}

interface NetworkGraphProps {
    data: {
        nodes: Node[];
        links: Link[];
    };
    width?: number;
    height?: number;
}

const NetworkGraph: React.FC<NetworkGraphProps> = ({ data, width = 600, height = 400 }) => {
    const svgRef = useRef<SVGSVGElement>(null);
    const [nodes, setNodes] = useState<Node[]>([]);
    const [links, setLinks] = useState<Link[]>([]);

    useEffect(() => {
        // Initialize simulation data
        if (!data.nodes.length) return;

        // Simple force-directed layout simulation (custom implementation to avoid d3 dependency bloat)
        // Initialize positions centered
        const newNodes = data.nodes.map(n => ({
            ...n,
            x: Math.random() * width,
            y: Math.random() * height,
            vx: 0,
            vy: 0
        }));

        const newLinks = data.links.map(l => ({ ...l }));

        setNodes(newNodes);
        setLinks(newLinks);

        // Run simple simulation tick
        // In a real app with d3-force, this would be robust. 
        // Here we just place them in a circular layout for visual stability if no library allowed.
        // Or we implement a basic repulsion loop.

        // Let's settle for a circular layout for stability and aesthetics without heavy math libs
        const centerX = width / 2;
        const centerY = height / 2;
        const radius = Math.min(width, height) / 3;

        const positionedNodes = newNodes.map((node, i) => {
            const angle = (i / newNodes.length) * 2 * Math.PI;
            return {
                ...node,
                x: centerX + radius * Math.cos(angle),
                y: centerY + radius * Math.sin(angle)
            };
        });
        setNodes(positionedNodes);

    }, [data, width, height]);

    if (!data?.nodes?.length) {
        return (
            <div className="flex items-center justify-center h-64 border border-white/10 rounded-xl bg-white/5">
                <span className="text-white/40">No network data available</span>
            </div>
        );
    }

    return (
        <div className="relative w-full h-full min-h-[400px] glass-panel rounded-xl overflow-hidden bg-slate-900/50">
            <svg ref={svgRef} width="100%" height="100%" viewBox={`0 0 ${width} ${height}`} className="w-full h-full">
                <defs>
                    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
                        <feGaussianBlur stdDeviation="2" result="blur" />
                        <feComposite in="SourceGraphic" in2="blur" operator="over" />
                    </filter>
                </defs>

                {/* Links */}
                {links.map((link, i) => {
                    const sourceNode = nodes.find(n => n.id === (typeof link.source === 'object' ? link.source.id : link.source));
                    const targetNode = nodes.find(n => n.id === (typeof link.target === 'object' ? link.target.id : link.target));

                    if (!sourceNode || !targetNode) return null;

                    return (
                        <line
                            key={i}
                            x1={sourceNode.x}
                            y1={sourceNode.y}
                            x2={targetNode.x}
                            y2={targetNode.y}
                            stroke="rgba(255,255,255,0.1)"
                            strokeWidth={1}
                        />
                    );
                })}

                {/* Nodes */}
                {nodes.map((node, i) => (
                    <g key={i} transform={`translate(${node.x},${node.y})`}>
                        {/* Glow effect */}
                        <circle
                            r={node.radius + 4}
                            fill={node.group === 1 ? "#3b82f6" : "#10b981"}
                            opacity="0.2"
                            filter="url(#glow)"
                        />
                        {/* Core node */}
                        <circle
                            r={node.radius}
                            fill={node.group === 1 ? "#3b82f6" : "#10b981"}
                            className="cursor-pointer hover:opacity-80 transition-opacity"
                        />
                        {/* Label */}
                        <text
                            dy={node.radius + 15}
                            textAnchor="middle"
                            fill="rgba(255,255,255,0.7)"
                            fontSize="10"
                            className="pointer-events-none select-none font-sans"
                        >
                            {node.id}
                        </text>
                    </g>
                ))}
            </svg>

            {/* Overlay Info */}
            <div className="absolute bottom-4 left-4 text-xs text-white/30 pointer-events-none">
                {nodes.length} Nodes • {links.length} Connections
            </div>
        </div>
    );
};

export default NetworkGraph;
