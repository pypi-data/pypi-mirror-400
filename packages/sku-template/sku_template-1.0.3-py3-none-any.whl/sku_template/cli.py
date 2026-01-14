"""
Command line interface for AppID Manager Client
"""
import argparse
import sys
import json
from .client import AppIdClient


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="AppID Manager Client CLI")
    parser.add_argument("--url", default="http://101.64.234.17:8888", help="Server URL")
    parser.add_argument("--timeout", type=int, default=5, help="Request timeout")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Health check command
    health_parser = subparsers.add_parser("health", help="Check service health")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Get AppID status")
    status_parser.add_argument("--product", help="Product name to filter")
    
    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize product")
    init_parser.add_argument("product", help="Product name")
    init_parser.add_argument("config", help="AppID config file (JSON)")
    
    # Acquire command
    acquire_parser = subparsers.add_parser("acquire", help="Acquire AppID")
    acquire_parser.add_argument("product", help="Product name")
    acquire_parser.add_argument("--max-retries", type=int, default=60, help="Max retries")
    acquire_parser.add_argument("--retry-interval", type=int, default=60, help="Retry interval")
    
    # Release command
    release_parser = subparsers.add_parser("release", help="Release AppID")
    release_parser.add_argument("product", help="Product name")
    release_parser.add_argument("appid", help="AppID to release")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Create client
    client = AppIdClient(args.url, args.timeout)
    
    try:
        if args.command == "health":
            if client.health_check():
                print("Service is healthy")
                sys.exit(0)
            else:
                print("Service is unhealthy")
                sys.exit(1)
        
        elif args.command == "status":
            status = client.get_status(args.product)
            if status:
                print(json.dumps(status, indent=2))
            else:
                print("Failed to get status")
                sys.exit(1)
        
        elif args.command == "init":
            try:
                with open(args.config, 'r') as f:
                    appids = json.load(f)
                if client.init_product(args.product, appids):
                    print(f"Product '{args.product}' initialized successfully")
                else:
                    print(f"Failed to initialize product '{args.product}'")
                    sys.exit(1)
            except FileNotFoundError:
                print(f"Config file not found: {args.config}")
                sys.exit(1)
            except json.JSONDecodeError:
                print(f"Invalid JSON in config file: {args.config}")
                sys.exit(1)
        
        elif args.command == "acquire":
            try:
                appid, vid, start_time, product_name = client.acquire_appid(
                    args.product, 
                    args.max_retries, 
                    args.retry_interval
                )
                result = {
                    "appid": appid,
                    "vid": vid,
                    "start_time": start_time,
                    "product_name": product_name
                }
                print(json.dumps(result))
            except Exception as e:
                print(f"Error acquiring AppID: {e}")
                sys.exit(1)
        
        elif args.command == "release":
            try:
                if client.release_appid(args.appid, args.product):
                    print(f"AppID '{args.appid}' released successfully")
                else:
                    print(f"Failed to release AppID '{args.appid}'")
                    sys.exit(1)
            except Exception as e:
                print(f"Error releasing AppID: {e}")
                sys.exit(1)
    
    except KeyboardInterrupt:
        print("\nOperation cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
