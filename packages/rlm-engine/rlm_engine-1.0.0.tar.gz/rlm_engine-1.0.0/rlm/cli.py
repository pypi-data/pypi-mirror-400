#!/usr/bin/env python3
"""Command-line interface for RLM."""
import sys
import json
import argparse
from pathlib import Path

from .core import RLM, RLMConfig
from .config import load_config, save_config, CONFIG_TEMPLATE, RLMSettings


def cmd_query(args):
    """Execute a query against a document."""
    settings = load_config(args.config)
    
    # Override with CLI args
    if args.backend:
        settings.backend = args.backend
    if args.model:
        settings.model = args.model
    if args.base_url:
        settings.base_url = args.base_url
    
    config = RLMConfig(
        max_iterations=args.max_iterations,
        max_depth=args.max_depth,
        temperature=args.temperature,
        verbose=args.verbose,
    )
    
    rlm = RLM(
        backend=settings.backend,
        model=settings.model,
        base_url=settings.base_url,
        api_key=settings.api_key,
        config=config,
    )
    
    # Get context
    if args.file:
        context = Path(args.file).read_text()
    elif args.stdin or not sys.stdin.isatty():
        context = sys.stdin.read()
    else:
        print("Error: No context provided. Use --file or pipe to stdin.", file=sys.stderr)
        sys.exit(1)
    
    try:
        result = rlm.completion(args.query, context)
        
        if args.json:
            output = {
                "answer": result.answer,
                "iterations": result.iterations,
                "llm_calls": result.total_llm_calls,
                "execution_time": result.execution_time,
                "success": result.success,
            }
            print(json.dumps(output, indent=2))
        else:
            print(result.answer)
            if args.verbose:
                print(f"\n---\nIterations: {result.iterations}")
                print(f"LLM Calls: {result.total_llm_calls}")
                print(f"Time: {result.execution_time:.2f}s")
    finally:
        rlm.close()


def cmd_serve(args):
    """Start the API server."""
    from .server import run_server
    
    settings = load_config(args.config)
    host = args.host or settings.server_host
    port = args.port or settings.server_port
    
    print(f"Starting RLM server on {host}:{port}")
    run_server(host=host, port=port)


def cmd_init(args):
    """Initialize a new config file."""
    config_path = args.output or "rlm.yaml"
    
    if Path(config_path).exists() and not args.force:
        print(f"Config file already exists: {config_path}")
        print("Use --force to overwrite.")
        sys.exit(1)
    
    with open(config_path, "w") as f:
        f.write(CONFIG_TEMPLATE.strip())
    
    print(f"Created config file: {config_path}")


def cmd_benchmark(args):
    """Run benchmarks."""
    from .benchmarks import run_benchmark
    
    settings = load_config(args.config)
    
    print("Running RLM benchmarks...")
    results = run_benchmark(
        backend=args.backend or settings.backend,
        model=args.model or settings.model,
        base_url=args.base_url or settings.base_url,
    )
    
    if args.output:
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to: {args.output}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="RLM - Recursive Language Model CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Query a file
  rlm query "What is the revenue?" --file report.txt
  
  # Query from stdin
  cat document.txt | rlm query "Summarize this"
  
  # Use specific model
  rlm query "Find dates" --file data.txt --backend vllm --base-url http://localhost:8000/v1
  
  # Start API server
  rlm serve --port 8080
  
  # Initialize config
  rlm init
        """,
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Query command
    query_parser = subparsers.add_parser("query", help="Execute a query")
    query_parser.add_argument("query", help="The question to answer")
    query_parser.add_argument("-f", "--file", help="Path to document file")
    query_parser.add_argument("--stdin", action="store_true", help="Read context from stdin")
    query_parser.add_argument("--backend", choices=["openai", "anthropic", "vllm", "ollama"])
    query_parser.add_argument("--model", help="Model name")
    query_parser.add_argument("--base-url", help="API base URL")
    query_parser.add_argument("--max-iterations", type=int, default=10)
    query_parser.add_argument("--max-depth", type=int, default=3)
    query_parser.add_argument("--temperature", type=float, default=0.7)
    query_parser.add_argument("-v", "--verbose", action="store_true")
    query_parser.add_argument("--json", action="store_true", help="Output as JSON")
    query_parser.add_argument("-c", "--config", help="Config file path")
    query_parser.set_defaults(func=cmd_query)
    
    # Serve command
    serve_parser = subparsers.add_parser("serve", help="Start API server")
    serve_parser.add_argument("--host", default="0.0.0.0")
    serve_parser.add_argument("--port", type=int, default=8080)
    serve_parser.add_argument("-c", "--config", help="Config file path")
    serve_parser.set_defaults(func=cmd_serve)
    
    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize config file")
    init_parser.add_argument("-o", "--output", help="Output path", default="rlm.yaml")
    init_parser.add_argument("--force", action="store_true", help="Overwrite existing")
    init_parser.set_defaults(func=cmd_init)
    
    # Benchmark command
    bench_parser = subparsers.add_parser("benchmark", help="Run benchmarks")
    bench_parser.add_argument("--backend", choices=["openai", "anthropic", "vllm", "ollama"])
    bench_parser.add_argument("--model", help="Model name")
    bench_parser.add_argument("--base-url", help="API base URL")
    bench_parser.add_argument("-o", "--output", help="Output JSON path")
    bench_parser.add_argument("-c", "--config", help="Config file path")
    bench_parser.set_defaults(func=cmd_benchmark)
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == "__main__":
    main()
