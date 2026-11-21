"""Initial Schema: Retailers, Products, Offers, Price History, Alerts, Sources, Runs

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-11-13 12:00:00.000000

"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Retailers
    op.create_table(
        'retailers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=150), nullable=False),
        sa.Column('website', sa.String(length=255), nullable=False),
        sa.Column('currency', sa.String(length=10), server_default='USD', nullable=False),
        sa.Column('country', sa.String(length=80), server_default='US', nullable=False),
        sa.Column('active', sa.Boolean(), server_default='1', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index('ix_retailers_id', 'retailers', ['id'], unique=False)

    # 2. Products
    op.create_table(
        'products',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('canonical_name', sa.String(length=250), nullable=False),
        sa.Column('brand', sa.String(length=120), server_default='', nullable=False),
        sa.Column('category', sa.String(length=100), server_default='', nullable=False),
        sa.Column('model_number', sa.String(length=120), nullable=True),
        sa.Column('gtin', sa.String(length=30), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('gtin')
    )
    op.create_index('ix_products_id', 'products', ['id'], unique=False)
    op.create_index('ix_products_canonical_name', 'products', ['canonical_name'], unique=False)
    op.create_index('ix_products_category', 'products', ['category'], unique=False)

    # 3. Data Sources
    op.create_table(
        'data_sources',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=120), nullable=False),
        sa.Column('source_type', sa.String(length=80), nullable=False),
        sa.Column('configuration', sa.JSON(), nullable=True),
        sa.Column('enabled', sa.Boolean(), server_default='1', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index('ix_data_sources_id', 'data_sources', ['id'], unique=False)

    # 4. Collection Runs
    op.create_table(
        'collection_runs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('source_id', sa.Integer(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(length=30), server_default='queued', nullable=False),
        sa.Column('records_extracted', sa.Integer(), server_default='0', nullable=False),
        sa.Column('records_loaded', sa.Integer(), server_default='0', nullable=False),
        sa.Column('error_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['source_id'], ['data_sources.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_collection_runs_id', 'collection_runs', ['id'], unique=False)

    # 5. Retailer Products
    op.create_table(
        'retailer_products',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('retailer_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('retailer_sku', sa.String(length=80), nullable=True),
        sa.Column('product_url', sa.String(length=500), nullable=True),
        sa.Column('retailer_product_name', sa.String(length=250), server_default='', nullable=False),
        sa.Column('current_price', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=10), server_default='USD', nullable=False),
        sa.Column('stock_status', sa.String(length=30), server_default='in_stock', nullable=False),
        sa.Column('last_checked_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
        sa.ForeignKeyConstraint(['retailer_id'], ['retailers.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('retailer_id', 'product_id', name='uq_retailer_product')
    )
    op.create_index('ix_retailer_products_id', 'retailer_products', ['id'], unique=False)

    # 6. Price History
    op.create_table(
        'price_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('retailer_product_id', sa.Integer(), nullable=False),
        sa.Column('observed_price', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('original_price', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('currency', sa.String(length=10), server_default='USD', nullable=False),
        sa.Column('stock_status', sa.String(length=30), server_default='in_stock', nullable=False),
        sa.Column('observed_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('collection_run_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['collection_run_id'], ['collection_runs.id'], ),
        sa.ForeignKeyConstraint(['retailer_product_id'], ['retailer_products.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('retailer_product_id', 'observed_at', 'observed_price', name='uq_price_history_observation')
    )
    op.create_index('ix_price_history_id', 'price_history', ['id'], unique=False)
    op.create_index('ix_price_history_observed_at', 'price_history', ['observed_at'], unique=False)

    # 7. Price Alerts
    op.create_table(
        'price_alerts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('retailer_product_id', sa.Integer(), nullable=True),
        sa.Column('alert_type', sa.String(length=50), nullable=False),
        sa.Column('previous_value', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('current_value', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('threshold', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('status', sa.String(length=30), server_default='active', nullable=False),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
        sa.ForeignKeyConstraint(['retailer_product_id'], ['retailer_products.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_price_alerts_id', 'price_alerts', ['id'], unique=False)
    op.create_index('ix_price_alerts_status', 'price_alerts', ['status'], unique=False)


def downgrade() -> None:
    op.drop_table('price_alerts')
    op.drop_table('price_history')
    op.drop_table('retailer_products')
    op.drop_table('collection_runs')
    op.drop_table('data_sources')
    op.drop_table('products')
    op.drop_table('retailers')
