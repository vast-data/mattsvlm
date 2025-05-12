```mermaid
flowchart TD
    %% Define Styles for Clarity
    classDef vastPlatform fill:#D6EAF8,stroke:#3498DB,stroke-width:2px;
    classDef insightEngine fill:#E8DAEF,stroke:#8E44AD,stroke-width:2px;
    classDef engineLayer fill:#F5EEF8,stroke:#BB8FCE,stroke-width:1px,stroke-dasharray: 5 5;
    classDef inputs fill:#FEF9E7,stroke:#F1C40F;
    classDef outputs fill:#E9F7EF,stroke:#2ECC71;
    classDef agents fill:#FDEDEC,stroke:#E74C3C;
    classDef nvidia fill:#E5E7E9,stroke:#839192,stroke-dasharray: 2 2;

    %% Inputs
    A[fa:fa-file-video Video Streams/Files]:::inputs

    %% InsightEngine Layer Subgraph
    subgraph VAST_InsightEngine_Layer [VAST InsightEngine Layer]:::engineLayer
        direction TB
        B[VAST InsightEngine]:::insightEngine

        %% Nested Subgraph for AI Agents within the Engine Layer
        subgraph AI_Agents [fa:fa-robot AI Agents Operating Within]:::agents
            direction LR
            C1(fa:fa-brain AI Agent)
            C2(fa:fa-brain AI Agent)
            C3(...)
        end

        %% NVIDIA Badge (Positioned within the subgraph)
        D(<i><small>fa:fa-microchip Accelerated by NVIDIA</small></i>):::nvidia

        %% Internal Connections (conceptual)
        B --- AI_Agents -- style AI_Agents stroke-width:0px; fill:none; %% Make agent subgraph visually contained
        B -.-> D %% Subtle link to badge

    end

    %% Foundation Layer
    E[fa:fa-database VAST Data Platform <br/> (Foundation)]:::vastPlatform

    %% Outputs
    subgraph Generated_Outputs [Outputs]:::outputs
        direction TB
        F[fa:fa-tags Rich Metadata]
        G[fa:fa-search-plus Searchable Vectors]
        H[fa:fa-lightbulb Insights]
        I[fa:fa-cogs Automated Actions]
    end

    %% Connections / Flow
    A -- Ingests --> B;          %% Video streams/files go into the InsightEngine
    B -- Processes using --> E; %% Engine utilizes the Platform foundation
    B -- Generates --> F;
    B -- Generates --> G;
    B -- Generates --> H;
    B -- Generates --> I;

    %% Link output subgraph conceptually from Engine
    B --> Generated_Outputs -- style Generated_Outputs stroke-width:0px; fill:none; %% Hide subgraph border for cleaner look
    ```