#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
希音钱包与提现数据模型
使用SQLAlchemy定义钱包余额表和提现记录表
优化：使用 ON DUPLICATE KEY UPDATE 批量 upsert 提高插入效率
"""

from sqlalchemy import create_engine, Column, Integer, String, BigInteger, DateTime, Text, Index, DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json
import time

# 创建基类
Base = declarative_base()


class SheinStoreWallet(Base):
    """
    希音店铺钱包余额表
    存储钱包余额信息（来自 /mws/mwms/sso/balance/query 接口）
    """
    __tablename__ = 'shein_store_wallet'

    # 主键ID
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='主键ID')

    # 关联店铺账号（唯一）
    store_username = Column(String(100), nullable=False, unique=True, comment='店铺账号')
    store_name = Column(String(200), nullable=True, comment='店铺名称')
    supplier_id = Column(BigInteger, nullable=True, comment='供应商ID')
    
    # ==================== 账户状态 ====================
    is_fp_account = Column(Integer, nullable=True, default=0, comment='是否FP账户(0-否,1-是)')
    deposit_flag = Column(Integer, nullable=True, comment='验证密码标志(1-需要验证,0-已验证)')
    
    # ==================== 余额信息 ====================
    currency = Column(String(20), nullable=True, comment='币种')
    withdrawable_amount = Column(DECIMAL(18, 2), nullable=True, comment='可提现金额')
    no_withdrawable_amount = Column(DECIMAL(18, 2), nullable=True, comment='不可提现金额')
    withdrawing_amount = Column(DECIMAL(18, 2), nullable=True, comment='提现中金额')
    balance_last_update_time = Column(BigInteger, nullable=True, comment='余额最后更新时间戳')
    auto_withdraw_state = Column(Integer, nullable=True, default=0, comment='自动提现状态(0-关闭,1-开启)')
    can_withdraw = Column(Integer, nullable=True, default=1, comment='是否可提现(0-否,1-是)')
    no_withdraw_reasons = Column(Text, nullable=True, comment='不可提现原因列表(JSON)')
    
    # ==================== 保证金信息 ====================
    deposit_currency = Column(String(20), nullable=True, comment='保证金币种')
    deposit_amount_paid = Column(DECIMAL(18, 2), nullable=True, comment='已缴保证金')
    deposit_amount_unpaid = Column(DECIMAL(18, 2), nullable=True, comment='未缴保证金')
    deposit_last_update_time = Column(BigInteger, nullable=True, comment='保证金最后更新时间戳')
    
    # ==================== 原始数据 ====================
    raw_balance_json = Column(Text, nullable=True, comment='余额原始数据(JSON)')
    raw_deposit_json = Column(Text, nullable=True, comment='保证金原始数据(JSON)')
    
    # ==================== 管理字段 ====================
    is_deleted = Column(Integer, nullable=True, default=0, comment='软删除标志(0-未删除,1-已删除)')
    remark = Column(String(500), nullable=True, comment='备注')
    
    # 时间戳
    created_at = Column(DateTime, nullable=True, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, nullable=True, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    # 创建索引
    __table_args__ = (
        Index('idx_wallet_supplier_id', 'supplier_id'),
        Index('idx_wallet_currency', 'currency'),
    )

    def __repr__(self):
        return f"<SheinStoreWallet(id={self.id}, store_username='{self.store_username}', withdrawable={self.withdrawable_amount})>"



class SheinStoreWithdraw(Base):
    """
    希音店铺提现记录表
    存储提现成功记录（来自 /mws/mwms/sso/withdraw/transferRecordList 接口）
    """
    __tablename__ = 'shein_store_withdraw'

    # 主键ID
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='主键ID')

    # 关联店铺账号
    store_username = Column(String(100), nullable=False, comment='店铺账号')
    store_name = Column(String(200), nullable=True, comment='店铺名称')
    supplier_id = Column(BigInteger, nullable=True, comment='供应商ID')
    
    # ==================== 提现单信息 ====================
    withdraw_no = Column(String(100), nullable=True, comment='提现单号')
    transfer_no = Column(String(100), nullable=True, unique=True, comment='转账单号(唯一)')
    
    # ==================== 金额信息 ====================
    currency = Column(String(20), nullable=True, comment='币种')
    net_amount = Column(DECIMAL(18, 2), nullable=True, comment='净金额')
    deposit_amount = Column(DECIMAL(18, 2), nullable=True, comment='保证金金额')
    commission_amount = Column(DECIMAL(18, 2), nullable=True, comment='手续费金额')
    receiving_currency = Column(String(20), nullable=True, comment='收款币种')
    receiving_amount = Column(DECIMAL(18, 2), nullable=True, comment='收款金额')
    exchange_rate = Column(String(50), nullable=True, comment='汇率')
    
    # ==================== 账户信息 ====================
    source_account_value = Column(String(100), nullable=True, comment='来源账户(脱敏)')
    account_area_code = Column(String(20), nullable=True, comment='账户地区代码')
    
    # ==================== 状态信息 ====================
    withdraw_status = Column(Integer, nullable=True, comment='提现状态(30-提现成功)')
    withdraw_status_desc = Column(String(50), nullable=True, comment='提现状态描述')
    fail_reason = Column(String(500), nullable=True, comment='失败原因')
    retry_flag = Column(Integer, nullable=True, default=0, comment='重试标志')
    
    # ==================== 提现来源 ====================
    withdraw_source = Column(Integer, nullable=True, comment='提现来源(0-人工提现)')
    withdraw_source_desc = Column(String(50), nullable=True, comment='提现来源描述')
    
    # ==================== 电子回单 ====================
    ele_ticket_status_code = Column(Integer, nullable=True, comment='电子回单状态码')
    ele_ticket_status_desc = Column(String(50), nullable=True, comment='电子回单状态描述')
    ele_ticket_button_code = Column(Integer, nullable=True, comment='电子回单按钮码')
    ele_ticket_button_desc = Column(String(50), nullable=True, comment='电子回单按钮描述')
    
    # ==================== 时间信息 ====================
    create_time = Column(BigInteger, nullable=True, comment='创建时间戳')
    last_update_time = Column(BigInteger, nullable=True, comment='最后更新时间戳')
    transfer_success_time = Column(BigInteger, nullable=True, comment='转账成功时间戳')
    
    # ==================== 管理字段 ====================
    is_deleted = Column(Integer, nullable=True, default=0, comment='软删除标志(0-未删除,1-已删除)')
    remark = Column(String(500), nullable=True, comment='备注')
    
    # 时间戳
    created_at = Column(DateTime, nullable=True, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, nullable=True, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    # 创建索引
    __table_args__ = (
        Index('idx_withdraw_supplier_id', 'supplier_id'),
        Index('idx_withdraw_store_username', 'store_username'),
        Index('idx_withdraw_no', 'withdraw_no'),
        Index('idx_withdraw_status', 'withdraw_status'),
        Index('idx_withdraw_create_time', 'create_time'),
    )

    def __repr__(self):
        return f"<SheinStoreWithdraw(id={self.id}, transfer_no='{self.transfer_no}', amount={self.net_amount})>"


class SheinStoreWalletManager:
    """
    钱包余额数据管理器
    使用 ON DUPLICATE KEY UPDATE 批量 upsert 提高效率
    """

    def __init__(self, database_url):
        print(f"连接数据库: {database_url}")
        self.engine = create_engine(
            database_url, 
            echo=False,
            pool_size=20,
            max_overflow=10,
            pool_recycle=3600,
            pool_pre_ping=True,
        )
        self.Session = sessionmaker(bind=self.engine, autoflush=False)

    def create_table(self):
        Base.metadata.create_all(self.engine)
        print("钱包余额表创建成功")

    def upsert_data(self, data_list, batch_size=500):
        """
        批量插入/更新钱包余额数据（幂等性）
        使用 ON DUPLICATE KEY UPDATE 实现
        
        Args:
            data_list (list): 钱包数据列表
            batch_size (int): 每批次插入的记录数
        """
        if not data_list:
            print("没有钱包余额数据需要插入")
            return 0
        
        # 准备数据，添加时间戳
        records = []
        for data in data_list:
            record = data.copy()
            record['created_at'] = datetime.now()
            record['updated_at'] = datetime.now()
            records.append(record)
        
        # 批量 upsert（带死锁重试）
        max_retries = 3
        total_count = 0
        
        with self.engine.connect() as conn:
            for i in range(0, len(records), batch_size):
                batch = records[i:i + batch_size]
                stmt = insert(SheinStoreWallet).values(batch)
                # ON DUPLICATE KEY UPDATE（store_username 是唯一键）
                stmt = stmt.on_duplicate_key_update(
                    store_name=stmt.inserted.store_name,
                    supplier_id=stmt.inserted.supplier_id,
                    is_fp_account=stmt.inserted.is_fp_account,
                    deposit_flag=stmt.inserted.deposit_flag,
                    currency=stmt.inserted.currency,
                    withdrawable_amount=stmt.inserted.withdrawable_amount,
                    no_withdrawable_amount=stmt.inserted.no_withdrawable_amount,
                    withdrawing_amount=stmt.inserted.withdrawing_amount,
                    balance_last_update_time=stmt.inserted.balance_last_update_time,
                    auto_withdraw_state=stmt.inserted.auto_withdraw_state,
                    can_withdraw=stmt.inserted.can_withdraw,
                    no_withdraw_reasons=stmt.inserted.no_withdraw_reasons,
                    deposit_currency=stmt.inserted.deposit_currency,
                    deposit_amount_paid=stmt.inserted.deposit_amount_paid,
                    deposit_amount_unpaid=stmt.inserted.deposit_amount_unpaid,
                    deposit_last_update_time=stmt.inserted.deposit_last_update_time,
                    raw_balance_json=stmt.inserted.raw_balance_json,
                    raw_deposit_json=stmt.inserted.raw_deposit_json,
                    updated_at=datetime.now()
                )
                # 死锁重试
                for retry in range(max_retries):
                    try:
                        conn.execute(stmt)
                        total_count += len(batch)
                        break
                    except OperationalError as e:
                        if 'Deadlock' in str(e) and retry < max_retries - 1:
                            print(f"[WARN] 死锁，重试 {retry + 1}/{max_retries}...")
                            time.sleep(1)
                            continue
                        raise
            conn.commit()
        
        print(f"[OK] 钱包余额: 成功 upsert {total_count} 条记录")
        return total_count

    def insert_data(self, data_list):
        """兼容旧接口，内部调用 upsert_data"""
        return self.upsert_data(data_list)

    def import_from_api_response(self, store_username, store_name, supplier_id, api_response):
        """
        从API响应导入钱包余额信息
        
        Args:
            store_username (str): 店铺账号
            store_name (str): 店铺名称
            supplier_id (int): 供应商ID
            api_response (dict): get_wallet_balance_detail 返回的数据
        
        Returns:
            dict: 解析后的记录数据（用于批量导入）
        """
        record = {
            'store_username': store_username,
            'store_name': store_name,
            'supplier_id': supplier_id,
            'is_fp_account': 1 if api_response.get('isFpAccount') else 0,
            'deposit_flag': api_response.get('depositFlag', 1),
            # 初始化所有字段，避免缺失导致 upsert 失败
            'currency': None,
            'withdrawable_amount': None,
            'no_withdrawable_amount': None,
            'withdrawing_amount': None,
            'balance_last_update_time': None,
            'auto_withdraw_state': 0,
            'can_withdraw': 1,
            'no_withdraw_reasons': '[]',
            'deposit_currency': None,
            'deposit_amount_paid': None,
            'deposit_amount_unpaid': None,
            'deposit_last_update_time': None,
            'raw_balance_json': None,
            'raw_deposit_json': None,
        }
        
        # 解析余额信息（取第一个）
        balance_list = api_response.get('balanceList', [])
        if balance_list:
            balance = balance_list[0]
            record.update({
                'currency': balance.get('currency'),
                'withdrawable_amount': balance.get('withdrawableAmount'),
                'no_withdrawable_amount': balance.get('noWithdrawableAmount'),
                'withdrawing_amount': balance.get('withdrawingAmount'),
                'balance_last_update_time': balance.get('lastUpdateTime'),
                'auto_withdraw_state': balance.get('autoWithdrawState', 0),
                'can_withdraw': 1 if balance.get('canWithdraw') else 0,
                'no_withdraw_reasons': json.dumps(balance.get('noWithdrawReasons', []), ensure_ascii=False),
            })
            record['raw_balance_json'] = json.dumps(balance_list, ensure_ascii=False)
        
        # 解析保证金信息（取第一个）
        deposit_list = api_response.get('depositList', [])
        if deposit_list:
            deposit = deposit_list[0]
            record.update({
                'deposit_currency': deposit.get('currency'),
                'deposit_amount_paid': deposit.get('depositAmountPaid'),
                'deposit_amount_unpaid': deposit.get('depositAmountUnPaid'),
                'deposit_last_update_time': deposit.get('lastUpdateTime'),
            })
            record['raw_deposit_json'] = json.dumps(deposit_list, ensure_ascii=False)
        
        return record
    
    def batch_import(self, wallet_data_list):
        """
        批量导入钱包余额数据
        
        Args:
            wallet_data_list (list): 包含 store_username, store_name, supplier_id, data 的字典列表
        
        Returns:
            int: 成功导入的记录数
        """
        if not wallet_data_list:
            print("没有钱包余额数据需要导入")
            return 0
        
        records = []
        for item in wallet_data_list:
            record = self.import_from_api_response(
                store_username=item['store_username'],
                store_name=item['store_name'],
                supplier_id=item['supplier_id'],
                api_response=item['data']
            )
            records.append(record)
        
        return self.upsert_data(records)

    def get_by_store_username(self, store_username, include_deleted=False):
        session = self.Session()
        try:
            query = session.query(SheinStoreWallet).filter(
                SheinStoreWallet.store_username == store_username
            )
            if not include_deleted:
                query = query.filter(SheinStoreWallet.is_deleted == 0)
            return query.first()
        finally:
            session.close()

    def get_all(self, include_deleted=False):
        session = self.Session()
        try:
            query = session.query(SheinStoreWallet)
            if not include_deleted:
                query = query.filter(SheinStoreWallet.is_deleted == 0)
            return query.all()
        finally:
            session.close()



class SheinStoreWithdrawManager:
    """
    提现记录数据管理器
    使用 ON DUPLICATE KEY UPDATE 批量 upsert 提高效率
    """

    def __init__(self, database_url):
        print(f"连接数据库: {database_url}")
        self.engine = create_engine(
            database_url, 
            echo=False,
            pool_size=20,
            max_overflow=10,
            pool_recycle=3600,
            pool_pre_ping=True,
        )
        self.Session = sessionmaker(bind=self.engine, autoflush=False)

    def create_table(self):
        Base.metadata.create_all(self.engine)
        print("提现记录表创建成功")

    def upsert_data(self, data_list, batch_size=500):
        """
        批量插入/更新提现记录数据（幂等性）
        使用 ON DUPLICATE KEY UPDATE 实现
        
        Args:
            data_list (list): 提现记录数据列表
            batch_size (int): 每批次插入的记录数
        """
        if not data_list:
            print("没有提现记录数据需要插入")
            return 0
        
        # 准备数据，添加时间戳
        records = []
        for data in data_list:
            record = data.copy()
            record['created_at'] = datetime.now()
            record['updated_at'] = datetime.now()
            records.append(record)
        
        # 批量 upsert（带死锁重试）
        max_retries = 3
        total_count = 0
        
        with self.engine.connect() as conn:
            for i in range(0, len(records), batch_size):
                batch = records[i:i + batch_size]
                stmt = insert(SheinStoreWithdraw).values(batch)
                # ON DUPLICATE KEY UPDATE（transfer_no 是唯一键）
                stmt = stmt.on_duplicate_key_update(
                    store_name=stmt.inserted.store_name,
                    supplier_id=stmt.inserted.supplier_id,
                    withdraw_no=stmt.inserted.withdraw_no,
                    currency=stmt.inserted.currency,
                    net_amount=stmt.inserted.net_amount,
                    deposit_amount=stmt.inserted.deposit_amount,
                    commission_amount=stmt.inserted.commission_amount,
                    receiving_currency=stmt.inserted.receiving_currency,
                    receiving_amount=stmt.inserted.receiving_amount,
                    exchange_rate=stmt.inserted.exchange_rate,
                    source_account_value=stmt.inserted.source_account_value,
                    account_area_code=stmt.inserted.account_area_code,
                    withdraw_status=stmt.inserted.withdraw_status,
                    withdraw_status_desc=stmt.inserted.withdraw_status_desc,
                    fail_reason=stmt.inserted.fail_reason,
                    retry_flag=stmt.inserted.retry_flag,
                    withdraw_source=stmt.inserted.withdraw_source,
                    withdraw_source_desc=stmt.inserted.withdraw_source_desc,
                    ele_ticket_status_code=stmt.inserted.ele_ticket_status_code,
                    ele_ticket_status_desc=stmt.inserted.ele_ticket_status_desc,
                    ele_ticket_button_code=stmt.inserted.ele_ticket_button_code,
                    ele_ticket_button_desc=stmt.inserted.ele_ticket_button_desc,
                    create_time=stmt.inserted.create_time,
                    last_update_time=stmt.inserted.last_update_time,
                    transfer_success_time=stmt.inserted.transfer_success_time,
                    updated_at=datetime.now()
                )
                # 死锁重试
                for retry in range(max_retries):
                    try:
                        conn.execute(stmt)
                        total_count += len(batch)
                        break
                    except OperationalError as e:
                        if 'Deadlock' in str(e) and retry < max_retries - 1:
                            print(f"[WARN] 死锁，重试 {retry + 1}/{max_retries}...")
                            time.sleep(1)
                            continue
                        raise
            conn.commit()
        
        print(f"[OK] 提现记录: 成功 upsert {total_count} 条记录")
        return total_count

    def insert_data(self, data_list):
        """兼容旧接口，内部调用 upsert_data"""
        return self.upsert_data(data_list)

    def import_from_api_response(self, store_username, store_name, supplier_id, api_response):
        """
        从API响应解析提现记录（不直接插入，返回记录列表）
        
        Args:
            store_username (str): 店铺账号
            store_name (str): 店铺名称
            supplier_id (int): 供应商ID
            api_response (dict): get_withdraw_success_list 返回的数据
        
        Returns:
            list: 解析后的记录列表（用于批量导入）
        """
        withdraw_list = api_response.get('list', [])
        
        if not withdraw_list:
            return []
        
        records = []
        for item in withdraw_list:
            record = {
                'store_username': store_username,
                'store_name': store_name,
                'supplier_id': supplier_id,
                
                # 提现单信息
                'withdraw_no': item.get('withdrawNo'),
                'transfer_no': item.get('transferNo'),
                
                # 金额信息
                'currency': item.get('currency'),
                'net_amount': item.get('netAmount'),
                'deposit_amount': item.get('depositAmount'),
                'commission_amount': item.get('commissionAmount'),
                'receiving_currency': item.get('receivingCurrency'),
                'receiving_amount': item.get('receivingAmount'),
                'exchange_rate': item.get('exchangeRate'),
                
                # 账户信息
                'source_account_value': item.get('sourceAccountValue'),
                'account_area_code': item.get('accountAreaCode'),
                
                # 状态信息
                'withdraw_status': item.get('withdrawStatus'),
                'withdraw_status_desc': item.get('withdrawStatusDesc'),
                'fail_reason': item.get('failReason'),
                'retry_flag': item.get('retryFlag', 0),
                
                # 提现来源
                'withdraw_source': item.get('withdrawSource'),
                'withdraw_source_desc': item.get('withdrawSourceDesc'),
                
                # 电子回单
                'ele_ticket_status_code': item.get('eleTicketStatusCode'),
                'ele_ticket_status_desc': item.get('eleTicketStatusDesc'),
                'ele_ticket_button_code': item.get('eleTicketButtonCode'),
                'ele_ticket_button_desc': item.get('eleTicketButtonDesc'),
                
                # 时间信息
                'create_time': item.get('createTime'),
                'last_update_time': item.get('lastUpdateTime'),
                'transfer_success_time': item.get('transferSuccessTime'),
            }
            records.append(record)
        
        return records
    
    def batch_import(self, withdraw_data_list):
        """
        批量导入提现记录数据
        
        Args:
            withdraw_data_list (list): 包含 store_username, store_name, supplier_id, data 的字典列表
        
        Returns:
            int: 成功导入的记录数
        """
        if not withdraw_data_list:
            print("没有提现记录数据需要导入")
            return 0
        
        all_records = []
        for item in withdraw_data_list:
            records = self.import_from_api_response(
                store_username=item['store_username'],
                store_name=item['store_name'],
                supplier_id=item['supplier_id'],
                api_response=item['data']
            )
            all_records.extend(records)
        
        if not all_records:
            print("没有提现记录数据需要导入")
            return 0
        
        return self.upsert_data(all_records)

    def get_by_store_username(self, store_username, include_deleted=False):
        session = self.Session()
        try:
            query = session.query(SheinStoreWithdraw).filter(
                SheinStoreWithdraw.store_username == store_username
            )
            if not include_deleted:
                query = query.filter(SheinStoreWithdraw.is_deleted == 0)
            return query.all()
        finally:
            session.close()

    def get_by_transfer_no(self, transfer_no, include_deleted=False):
        session = self.Session()
        try:
            query = session.query(SheinStoreWithdraw).filter(
                SheinStoreWithdraw.transfer_no == transfer_no
            )
            if not include_deleted:
                query = query.filter(SheinStoreWithdraw.is_deleted == 0)
            return query.first()
        finally:
            session.close()

    def get_all(self, include_deleted=False):
        session = self.Session()
        try:
            query = session.query(SheinStoreWithdraw)
            if not include_deleted:
                query = query.filter(SheinStoreWithdraw.is_deleted == 0)
            return query.all()
        finally:
            session.close()

    def get_by_date_range(self, store_username, start_time, end_time, include_deleted=False):
        """
        按时间范围查询提现记录
        
        Args:
            store_username (str): 店铺账号
            start_time (int): 开始时间戳（毫秒）
            end_time (int): 结束时间戳（毫秒）
        """
        session = self.Session()
        try:
            query = session.query(SheinStoreWithdraw).filter(
                SheinStoreWithdraw.store_username == store_username,
                SheinStoreWithdraw.create_time >= start_time,
                SheinStoreWithdraw.create_time <= end_time
            )
            if not include_deleted:
                query = query.filter(SheinStoreWithdraw.is_deleted == 0)
            return query.order_by(SheinStoreWithdraw.create_time.desc()).all()
        finally:
            session.close()


# ==================== 便捷函数 ====================

_wallet_manager = None
_withdraw_manager = None


def get_wallet_manager(database_url):
    global _wallet_manager
    if _wallet_manager is None:
        _wallet_manager = SheinStoreWalletManager(database_url)
    return _wallet_manager


def get_withdraw_manager(database_url):
    global _withdraw_manager
    if _withdraw_manager is None:
        _withdraw_manager = SheinStoreWithdrawManager(database_url)
    return _withdraw_manager


if __name__ == '__main__':
    # 测试代码
    database_url = "mysql+pymysql://root:123wyk@47.83.212.3:3306/lz"

    # 创建钱包余额表
    wallet_manager = SheinStoreWalletManager(database_url)
    wallet_manager.create_table()
    
    # 创建提现记录表
    withdraw_manager = SheinStoreWithdrawManager(database_url)
    withdraw_manager.create_table()
    
    print("表创建完成")
