#!/usr/bin/env python3
"""
CLI for managing GRKMemory API tokens.

Usage:
    python -m grkmemory.auth.cli create --name "My App"
    python -m grkmemory.auth.cli list
    python -m grkmemory.auth.cli revoke <token_id>
    python -m grkmemory.auth.cli validate <api_key>
"""

import argparse
import sys
from datetime import datetime

from .token_manager import TokenManager
from .auth import GRKAuth


def create_token(args):
    """Create a new API token."""
    auth = GRKAuth(args.file)
    
    permissions = args.permissions.split(",") if args.permissions else ["read", "write"]
    
    api_key = auth.create_api_key(
        name=args.name,
        permissions=permissions,
        expires_days=args.expires,
        rate_limit=args.rate_limit or 0
    )
    
    print("\n✅ Token criado com sucesso!")
    print("-" * 50)
    print(f"📛 Nome: {args.name}")
    print(f"🔑 API Key: {api_key}")
    print(f"🛡️ Permissões: {', '.join(permissions)}")
    if args.expires:
        print(f"⏰ Expira em: {args.expires} dias")
    if args.rate_limit:
        print(f"📊 Rate limit: {args.rate_limit} req/min")
    print("-" * 50)
    print("\n⚠️ IMPORTANTE: Salve a API Key agora!")
    print("   Ela não será mostrada novamente.")


def list_tokens(args):
    """List all tokens."""
    manager = TokenManager(args.file)
    tokens = manager.list_tokens(include_inactive=args.all)
    
    if not tokens:
        print("\n📭 Nenhum token encontrado.")
        return
    
    print(f"\n📋 Tokens ({len(tokens)}):")
    print("-" * 70)
    
    for token in tokens:
        status = "🟢 Ativo" if token.is_active else "🔴 Revogado"
        expired = " (EXPIRADO)" if token.is_expired() else ""
        
        print(f"\n{status}{expired}")
        print(f"   ID: {token.token_id}")
        print(f"   Nome: {token.name}")
        print(f"   Permissões: {', '.join(token.permissions)}")
        print(f"   Criado: {token.created_at[:19]}")
        if token.expires_at:
            print(f"   Expira: {token.expires_at[:19]}")
        if token.last_used:
            print(f"   Último uso: {token.last_used[:19]}")
        if token.rate_limit:
            print(f"   Rate limit: {token.rate_limit} req/min")
    
    print("-" * 70)


def revoke_token(args):
    """Revoke a token."""
    manager = TokenManager(args.file)
    
    if manager.revoke_token(args.token_id):
        print(f"\n✅ Token {args.token_id} revogado com sucesso!")
    else:
        print(f"\n❌ Token {args.token_id} não encontrado.")
        sys.exit(1)


def delete_token(args):
    """Delete a token permanently."""
    manager = TokenManager(args.file)
    
    # Confirm
    if not args.force:
        confirm = input(f"⚠️ Tem certeza que deseja DELETAR permanentemente o token {args.token_id}? (s/N): ")
        if confirm.lower() != 's':
            print("Operação cancelada.")
            return
    
    if manager.delete_token(args.token_id):
        print(f"\n✅ Token {args.token_id} deletado permanentemente!")
    else:
        print(f"\n❌ Token {args.token_id} não encontrado.")
        sys.exit(1)


def validate_token(args):
    """Validate an API key."""
    manager = TokenManager(args.file)
    
    token = manager.validate_token(args.api_key)
    
    if token:
        print("\n✅ API Key válida!")
        print("-" * 50)
        print(f"   Nome: {token.name}")
        print(f"   ID: {token.token_id}")
        print(f"   Permissões: {', '.join(token.permissions)}")
        print(f"   Criado: {token.created_at[:19]}")
        if token.expires_at:
            print(f"   Expira: {token.expires_at[:19]}")
        print("-" * 50)
    else:
        print("\n❌ API Key inválida ou expirada!")
        sys.exit(1)


def regenerate_key(args):
    """Regenerate API key for a token."""
    manager = TokenManager(args.file)
    
    new_key = manager.regenerate_key(args.token_id)
    
    if new_key:
        print(f"\n✅ Nova API Key gerada!")
        print("-" * 50)
        print(f"🔑 Nova API Key: {new_key}")
        print("-" * 50)
        print("\n⚠️ IMPORTANTE: A API Key antiga não funciona mais!")
        print("   Salve a nova chave agora.")
    else:
        print(f"\n❌ Token {args.token_id} não encontrado.")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="GRKMemory Token Manager CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  Criar token:      python -m grkmemory.auth.cli create --name "Meu App"
  Listar tokens:    python -m grkmemory.auth.cli list
  Revogar token:    python -m grkmemory.auth.cli revoke tok_abc123
  Validar API key:  python -m grkmemory.auth.cli validate grk_xyz...
        """
    )
    
    parser.add_argument(
        "--file", "-f",
        default="grkmemory_tokens.json",
        help="Arquivo de tokens (default: grkmemory_tokens.json)"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Comandos")
    
    # Create
    create_parser = subparsers.add_parser("create", help="Criar novo token")
    create_parser.add_argument("--name", "-n", required=True, help="Nome do token")
    create_parser.add_argument(
        "--permissions", "-p",
        help="Permissões separadas por vírgula (default: read,write)"
    )
    create_parser.add_argument(
        "--expires", "-e",
        type=int,
        help="Dias até expirar"
    )
    create_parser.add_argument(
        "--rate-limit", "-r",
        type=int,
        help="Requisições por minuto"
    )
    create_parser.set_defaults(func=create_token)
    
    # List
    list_parser = subparsers.add_parser("list", help="Listar tokens")
    list_parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="Incluir tokens revogados"
    )
    list_parser.set_defaults(func=list_tokens)
    
    # Revoke
    revoke_parser = subparsers.add_parser("revoke", help="Revogar token")
    revoke_parser.add_argument("token_id", help="ID do token")
    revoke_parser.set_defaults(func=revoke_token)
    
    # Delete
    delete_parser = subparsers.add_parser("delete", help="Deletar token permanentemente")
    delete_parser.add_argument("token_id", help="ID do token")
    delete_parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="Não pedir confirmação"
    )
    delete_parser.set_defaults(func=delete_token)
    
    # Validate
    validate_parser = subparsers.add_parser("validate", help="Validar API key")
    validate_parser.add_argument("api_key", help="API key para validar")
    validate_parser.set_defaults(func=validate_token)
    
    # Regenerate
    regen_parser = subparsers.add_parser("regenerate", help="Regenerar API key")
    regen_parser.add_argument("token_id", help="ID do token")
    regen_parser.set_defaults(func=regenerate_key)
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == "__main__":
    main()
