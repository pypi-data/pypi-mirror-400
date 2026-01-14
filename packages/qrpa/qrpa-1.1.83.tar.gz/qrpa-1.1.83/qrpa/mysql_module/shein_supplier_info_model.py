#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
供应商信息数据模型
使用SQLAlchemy定义供应商公司信息表和财务信息表
"""

from sqlalchemy import create_engine, Column, Integer, String, BigInteger, DateTime, Text, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json

# 创建基类
Base = declarative_base()


class SheinSupplierCompany(Base):
    """
    希音供应商公司信息表
    存储供应商公司信息（来自 /mip-eur-api/supplier/companyInfo/detail 接口）
    """
    __tablename__ = 'shein_store_company'

    # 主键ID
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='主键ID')

    # 关联店铺账号（唯一）
    store_username = Column(String(100), nullable=False, unique=True, comment='店铺账号')
    
    # ==================== 供应商基本信息 ====================
    supplier_id = Column(BigInteger, nullable=True, comment='供应商ID')
    supplier_type = Column(Integer, nullable=True, comment='供应商类型(1-个人,2-公司)')
    supplier_type_title = Column(String(50), nullable=True, comment='供应商类型名称')
    supplier_reg_area = Column(String(20), nullable=True, comment='供应商注册地区')
    
    # ==================== 营业执照信息 ====================
    company = Column(String(500), nullable=True, comment='公司名称')
    business_license = Column(BigInteger, nullable=True, comment='营业执照文件ID')
    business_license_name = Column(String(200), nullable=True, comment='营业执照文件名')
    business_license_url = Column(String(1000), nullable=True, comment='营业执照图片URL')
    business_license_type = Column(String(20), nullable=True, comment='营业执照类型')
    business_license_type_title = Column(String(100), nullable=True, comment='营业执照类型名称')
    code_register_no = Column(String(100), nullable=True, comment='统一社会信用代码')
    country_code = Column(String(20), nullable=True, comment='国家代码')
    country_code_title = Column(String(100), nullable=True, comment='国家名称')
    district_id = Column(BigInteger, nullable=True, comment='地区ID')
    district_name = Column(String(200), nullable=True, comment='地区名称')
    business_license_address = Column(String(500), nullable=True, comment='营业执照地址')
    business_license_postal_code = Column(String(20), nullable=True, comment='营业执照邮编')
    set_time = Column(String(20), nullable=True, comment='成立日期')
    
    # ==================== 法人信息 ====================
    legal_person_name = Column(String(100), nullable=True, comment='法人姓名')
    legal_person_nationality = Column(String(20), nullable=True, comment='法人国籍代码')
    legal_person_nationality_name = Column(String(100), nullable=True, comment='法人国籍名称')
    legal_person_cert_type = Column(Integer, nullable=True, comment='法人证件类型(1-身份证)')
    legal_person_cert_type_title = Column(String(50), nullable=True, comment='法人证件类型名称')
    legal_person_id_num = Column(String(50), nullable=True, comment='法人证件号码')
    legal_person_id_card_front = Column(BigInteger, nullable=True, comment='法人身份证正面文件ID')
    legal_person_id_card_front_url = Column(String(1000), nullable=True, comment='法人身份证正面图片URL')
    legal_person_id_card_back = Column(BigInteger, nullable=True, comment='法人身份证反面文件ID')
    legal_person_id_card_back_url = Column(String(1000), nullable=True, comment='法人身份证反面图片URL')
    legal_person_birth = Column(String(20), nullable=True, comment='法人出生日期')
    legal_person_telephone = Column(String(50), nullable=True, comment='法人电话')
    legal_person_telephone_area_code = Column(String(20), nullable=True, comment='法人电话区号')
    legal_person_telephone_area_code_title = Column(String(50), nullable=True, comment='法人电话区号名称')
    legal_person_email = Column(String(200), nullable=True, comment='法人邮箱')
    
    # 法人银行信息
    legal_person_bank_province = Column(String(20), nullable=True, comment='法人银行省份代码')
    legal_person_bank_province_name = Column(String(100), nullable=True, comment='法人银行省份名称')
    legal_person_bank_city = Column(String(20), nullable=True, comment='法人银行城市代码')
    legal_person_bank_city_name = Column(String(100), nullable=True, comment='法人银行城市名称')
    legal_person_bank_code = Column(String(20), nullable=True, comment='法人银行代码')
    legal_person_bank_name = Column(String(100), nullable=True, comment='法人银行名称')
    legal_person_bank_account = Column(String(50), nullable=True, comment='法人银行账号')
    
    # ==================== 实际控制人信息 ====================
    controller_list_json = Column(Text, nullable=True, comment='实际控制人列表(JSON)')
    
    # ==================== 合作信息 ====================
    has_worked_cbec = Column(String(10), nullable=True, comment='是否有跨境电商经验(1-是,2-否)')
    has_factory = Column(String(10), nullable=True, comment='是否有工厂(1-是,2-否)')
    cooperation_cross_border_json = Column(Text, nullable=True, comment='合作跨境平台列表(JSON)')
    
    # ==================== 变更信息 ====================
    change_count = Column(Integer, nullable=True, comment='变更次数')
    last_change_status = Column(Integer, nullable=True, comment='最后变更状态')
    last_change_status_name = Column(String(50), nullable=True, comment='最后变更状态名称')
    last_apply_no = Column(String(100), nullable=True, comment='最后申请编号')
    last_apply_time = Column(String(50), nullable=True, comment='最后申请时间')
    
    # ==================== 管理字段 ====================
    is_deleted = Column(Integer, nullable=True, default=0, comment='软删除标志(0-未删除,1-已删除)')
    remark = Column(String(500), nullable=True, comment='备注')
    
    # 时间戳
    created_at = Column(DateTime, nullable=True, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, nullable=True, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    # 创建索引
    __table_args__ = (
        Index('idx_company_supplier_id', 'supplier_id'),
        Index('idx_company_name', 'company'),
        Index('idx_company_code_register_no', 'code_register_no'),
    )

    def __repr__(self):
        return f"<SheinSupplierCompany(id={self.id}, store_username='{self.store_username}', company='{self.company}')>"


class SheinSupplierFinance(Base):
    """
    希音供应商财务信息表
    存储供应商财务信息（来自 /mip-eur-api/supplier/finance/detail 接口）
    """
    __tablename__ = 'shein_store_finance'

    # 主键ID
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='主键ID')

    # 关联店铺账号（唯一）
    store_username = Column(String(100), nullable=False, unique=True, comment='店铺账号')
    
    # ==================== 供应商基本信息 ====================
    supplier_id = Column(BigInteger, nullable=True, comment='供应商ID')
    category_id = Column(BigInteger, nullable=True, comment='类目ID')
    category_name = Column(String(200), nullable=True, comment='类目名称')
    parent_category_id = Column(BigInteger, nullable=True, comment='父类目ID')
    
    # ==================== 结算信息 ====================
    pay_currency_id = Column(Integer, nullable=True, comment='结算币种ID')
    pay_currency_name = Column(String(50), nullable=True, comment='结算币种名称')
    exchange_rate_type = Column(String(10), nullable=True, comment='汇率类型')
    exchange_rate_type_name = Column(String(50), nullable=True, comment='汇率类型名称')
    bank_account_tel = Column(String(50), nullable=True, comment='银行账户联系电话')
    
    # ==================== 默认收款账户信息 ====================
    default_account_id = Column(BigInteger, nullable=True, comment='默认账户ID')
    default_account_type = Column(String(10), nullable=True, comment='默认账户类型(1-非对公)')
    default_account_type_name = Column(String(50), nullable=True, comment='默认账户类型名称')
    default_location = Column(String(10), nullable=True, comment='默认账户地区(1-中国大陆)')
    default_location_name = Column(String(100), nullable=True, comment='默认账户地区名称')
    default_province = Column(String(20), nullable=True, comment='默认账户省份代码')
    default_province_name = Column(String(100), nullable=True, comment='默认账户省份名称')
    default_city = Column(String(20), nullable=True, comment='默认账户城市代码')
    default_city_name = Column(String(100), nullable=True, comment='默认账户城市名称')
    default_bank_code = Column(String(20), nullable=True, comment='默认银行代码')
    default_bank_name = Column(String(100), nullable=True, comment='默认银行名称')
    default_branch_code = Column(String(50), nullable=True, comment='默认支行代码')
    default_branch_name = Column(String(200), nullable=True, comment='默认支行名称')
    default_bank_account = Column(String(50), nullable=True, comment='默认银行账号')
    default_bank_account_name = Column(String(100), nullable=True, comment='默认银行账户名')
    default_bank_account_id_num = Column(String(50), nullable=True, comment='默认账户持有人证件号')
    default_bank_card_front = Column(BigInteger, nullable=True, comment='默认银行卡正面文件ID')
    default_bank_card_front_url = Column(String(1000), nullable=True, comment='默认银行卡正面图片URL')
    default_id_card_front = Column(BigInteger, nullable=True, comment='默认账户持有人身份证正面文件ID')
    default_id_card_front_url = Column(String(1000), nullable=True, comment='默认账户持有人身份证正面图片URL')
    default_id_card_back = Column(BigInteger, nullable=True, comment='默认账户持有人身份证反面文件ID')
    default_id_card_back_url = Column(String(1000), nullable=True, comment='默认账户持有人身份证反面图片URL')
    default_account_status = Column(Integer, nullable=True, comment='默认账户状态')
    default_account_status_name = Column(String(50), nullable=True, comment='默认账户状态名称')
    default_valid_status = Column(Integer, nullable=True, comment='默认账户有效状态')
    default_payee_legal_person_rel = Column(String(10), nullable=True, comment='收款人与法人关系')
    default_payee_legal_person_rel_name = Column(String(50), nullable=True, comment='收款人与法人关系名称')
    default_payee_country_code = Column(String(20), nullable=True, comment='收款人国家代码')
    default_payee_born_country_code = Column(String(20), nullable=True, comment='收款人出生国家代码')
    default_payee_born_country_code_title = Column(String(100), nullable=True, comment='收款人出生国家名称')
    
    # ==================== 所有账户列表 ====================
    account_list_json = Column(Text, nullable=True, comment='所有银行账户列表(JSON)')
    account_count = Column(Integer, nullable=True, comment='银行账户数量')
    
    # ==================== 变更信息 ====================
    change_count = Column(Integer, nullable=True, comment='变更次数')
    last_change_status = Column(Integer, nullable=True, comment='最后变更状态')
    last_change_status_name = Column(String(50), nullable=True, comment='最后变更状态名称')
    last_apply_time = Column(String(50), nullable=True, comment='最后申请时间')
    last_approval_type = Column(String(20), nullable=True, comment='最后审批类型')
    last_approval_id = Column(BigInteger, nullable=True, comment='最后审批ID')
    
    # ==================== 管理字段 ====================
    is_deleted = Column(Integer, nullable=True, default=0, comment='软删除标志(0-未删除,1-已删除)')
    remark = Column(String(500), nullable=True, comment='备注')
    
    # 时间戳
    created_at = Column(DateTime, nullable=True, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, nullable=True, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    # 创建索引
    __table_args__ = (
        Index('idx_finance_supplier_id', 'supplier_id'),
        Index('idx_finance_category_id', 'category_id'),
    )

    def __repr__(self):
        return f"<SheinSupplierFinance(id={self.id}, store_username='{self.store_username}', supplier_id={self.supplier_id})>"


class SheinSupplierCompanyManager:
    """
    供应商公司信息数据管理器
    """

    def __init__(self, database_url):
        print(f"连接数据库: {database_url}")
        self.engine = create_engine(database_url, echo=False)
        self.Session = sessionmaker(bind=self.engine)

    def create_table(self):
        Base.metadata.create_all(self.engine)
        print("供应商公司信息表创建成功")

    def insert_data(self, data_list):
        session = self.Session()
        try:
            insert_count = 0
            update_count = 0
            
            for data in data_list:
                existing = session.query(SheinSupplierCompany).filter(
                    SheinSupplierCompany.store_username == data.get('store_username')
                ).first()

                if existing:
                    exclude_fields = {'is_deleted'}
                    for key, value in data.items():
                        if key not in exclude_fields:
                            setattr(existing, key, value)
                    setattr(existing, 'updated_at', datetime.now())
                    update_count += 1
                else:
                    new_record = SheinSupplierCompany(**data)
                    session.add(new_record)
                    insert_count += 1

            session.commit()
            print(f"公司信息: 成功插入 {insert_count} 条记录，更新 {update_count} 条记录")
            return insert_count
        except Exception as e:
            session.rollback()
            print(f"插入数据失败: {e}")
            raise
        finally:
            session.close()

    def import_from_api_response(self, store_username, api_response):
        """
        从API响应导入公司信息
        
        Args:
            store_username (str): 店铺账号
            api_response (dict): /mip-eur-api/supplier/companyInfo/detail 接口返回的info字段
        """
        condition = api_response.get('condition', {})
        
        record = {
            'store_username': store_username,
            'supplier_id': api_response.get('supplierId'),
            'supplier_type': api_response.get('supplierType'),
            'supplier_type_title': api_response.get('supplierTypeTitle'),
            'supplier_reg_area': condition.get('supplierRegArea'),
            
            # 营业执照信息
            'company': condition.get('company'),
            'business_license': condition.get('businessLicense'),
            'business_license_name': condition.get('businessLicenseName'),
            'business_license_url': condition.get('businessLicensePathOss', {}).get('url') if condition.get('businessLicensePathOss') else condition.get('businessLicensePath'),
            'business_license_type': condition.get('businessLicenseType'),
            'business_license_type_title': condition.get('businessLicenseTypeTitle'),
            'code_register_no': condition.get('codeRegisterNo'),
            'country_code': condition.get('countryCode'),
            'country_code_title': condition.get('countryCodeTitle'),
            'district_id': condition.get('districtId'),
            'district_name': condition.get('districtName'),
            'business_license_address': condition.get('businessLicenseAddress'),
            'business_license_postal_code': condition.get('businessLicensePostalCode'),
            'set_time': condition.get('setTime'),
            
            # 法人信息
            'legal_person_name': condition.get('legalPersonName'),
            'legal_person_nationality': condition.get('legalPersonNationality'),
            'legal_person_nationality_name': condition.get('legalPersonNationalityName'),
            'legal_person_cert_type': condition.get('legalPersonCertType'),
            'legal_person_cert_type_title': condition.get('legalPersonCertTypeTitle'),
            'legal_person_id_num': condition.get('legalPersonIdNum'),
            'legal_person_id_card_front': condition.get('legalPersonIdA'),
            'legal_person_id_card_front_url': condition.get('legalPersonIdAPathOss', {}).get('url') if condition.get('legalPersonIdAPathOss') else condition.get('legalPersonIdAPath'),
            'legal_person_id_card_back': condition.get('legalPersonIdB'),
            'legal_person_id_card_back_url': condition.get('legalPersonIdBPathOss', {}).get('url') if condition.get('legalPersonIdBPathOss') else condition.get('legalPersonIdBPath'),
            'legal_person_birth': condition.get('legalPersonBirth'),
            'legal_person_telephone': condition.get('legalPersonTelephone'),
            'legal_person_telephone_area_code': condition.get('legalPersonTelephoneAreaCode'),
            'legal_person_telephone_area_code_title': condition.get('legalPersonTelephoneAreaCodeTitle'),
            'legal_person_email': condition.get('legalPersonEmail'),
            
            # 法人银行信息
            'legal_person_bank_province': condition.get('legalPersonBankProvince'),
            'legal_person_bank_province_name': condition.get('legalPersonBankProvinceName'),
            'legal_person_bank_city': condition.get('legalPersonBankCity'),
            'legal_person_bank_city_name': condition.get('legalPersonBankCityName'),
            'legal_person_bank_code': condition.get('legalPersonBankCode'),
            'legal_person_bank_name': condition.get('legalPersonBankName'),
            'legal_person_bank_account': condition.get('legalPersonBankAccount'),
            
            # 实际控制人
            'controller_list_json': json.dumps(condition.get('controllerList', []), ensure_ascii=False) if condition.get('controllerList') else None,
            
            # 合作信息
            'has_worked_cbec': condition.get('hasWorkedCbec'),
            'has_factory': condition.get('hasFactory'),
            'cooperation_cross_border_json': json.dumps(condition.get('cooperationCrossCorderSupplier', []), ensure_ascii=False) if condition.get('cooperationCrossCorderSupplier') else None,
            
            # 变更信息
            'change_count': condition.get('changeCount'),
            'last_change_status': condition.get('lastChangeStatus'),
            'last_change_status_name': condition.get('lastChangeStatusName'),
            'last_apply_no': condition.get('lastApplyNo'),
            'last_apply_time': condition.get('lastApplyTime'),
        }
        
        return self.insert_data([record])

    def get_by_store_username(self, store_username, include_deleted=False):
        session = self.Session()
        try:
            query = session.query(SheinSupplierCompany).filter(
                SheinSupplierCompany.store_username == store_username
            )
            if not include_deleted:
                query = query.filter(SheinSupplierCompany.is_deleted == 0)
            return query.first()
        finally:
            session.close()

    def get_all(self, include_deleted=False):
        session = self.Session()
        try:
            query = session.query(SheinSupplierCompany)
            if not include_deleted:
                query = query.filter(SheinSupplierCompany.is_deleted == 0)
            return query.all()
        finally:
            session.close()


class SheinSupplierFinanceManager:
    """
    供应商财务信息数据管理器
    """

    def __init__(self, database_url):
        print(f"连接数据库: {database_url}")
        self.engine = create_engine(database_url, echo=False)
        self.Session = sessionmaker(bind=self.engine)

    def create_table(self):
        Base.metadata.create_all(self.engine)
        print("供应商财务信息表创建成功")

    def insert_data(self, data_list):
        session = self.Session()
        try:
            insert_count = 0
            update_count = 0
            
            for data in data_list:
                existing = session.query(SheinSupplierFinance).filter(
                    SheinSupplierFinance.store_username == data.get('store_username')
                ).first()

                if existing:
                    exclude_fields = {'is_deleted'}
                    for key, value in data.items():
                        if key not in exclude_fields:
                            setattr(existing, key, value)
                    setattr(existing, 'updated_at', datetime.now())
                    update_count += 1
                else:
                    new_record = SheinSupplierFinance(**data)
                    session.add(new_record)
                    insert_count += 1

            session.commit()
            print(f"财务信息: 成功插入 {insert_count} 条记录，更新 {update_count} 条记录")
            return insert_count
        except Exception as e:
            session.rollback()
            print(f"插入数据失败: {e}")
            raise
        finally:
            session.close()

    def import_from_api_response(self, store_username, api_response):
        """
        从API响应导入财务信息
        
        Args:
            store_username (str): 店铺账号
            api_response (dict): /mip-eur-api/supplier/finance/detail 接口返回的info字段
        """
        account_list = api_response.get('accountList', [])
        
        # 找到默认账户
        default_account = None
        for account in account_list:
            if account.get('defaultAccount') == 1:
                default_account = account
                break
        
        record = {
            'store_username': store_username,
            'supplier_id': api_response.get('supplierId'),
            'category_id': api_response.get('categoryId'),
            'category_name': api_response.get('categoryName'),
            'parent_category_id': api_response.get('parentCategoryId'),
            
            # 结算信息
            'pay_currency_id': api_response.get('payCurrencyId'),
            'pay_currency_name': api_response.get('payCurrencyName'),
            'exchange_rate_type': api_response.get('exchangeRateType'),
            'exchange_rate_type_name': api_response.get('exchangeRateTypeName'),
            'bank_account_tel': api_response.get('bankAccountTel'),
            
            # 变更信息
            'change_count': api_response.get('changeCount'),
            'last_change_status': api_response.get('lastChangeStatus'),
            'last_change_status_name': api_response.get('lastChangeStatusName'),
            'last_apply_time': api_response.get('lastApplyTime'),
            'last_approval_type': api_response.get('lastApprovalType'),
            'last_approval_id': api_response.get('lastApprovalId'),
            
            # 账户列表
            'account_list_json': json.dumps(account_list, ensure_ascii=False) if account_list else None,
            'account_count': len(account_list),
        }
        
        # 默认账户信息
        if default_account:
            # 获取银行卡图片URL (bankAccountFileVo.urlOss.url)
            bank_card_front_url = None
            bank_account_file_vo = default_account.get('bankAccountFileVo')
            if bank_account_file_vo:
                url_oss = bank_account_file_vo.get('urlOss')
                if url_oss:
                    bank_card_front_url = url_oss.get('url')
                if not bank_card_front_url:
                    bank_card_front_url = bank_account_file_vo.get('url')
            
            # 获取身份证正面图片URL (bankAccountIdCardFileVo.urlOss.url)
            id_card_front_url = None
            bank_account_id_card_file_vo = default_account.get('bankAccountIdCardFileVo')
            if bank_account_id_card_file_vo:
                url_oss = bank_account_id_card_file_vo.get('urlOss')
                if url_oss:
                    id_card_front_url = url_oss.get('url')
                if not id_card_front_url:
                    id_card_front_url = bank_account_id_card_file_vo.get('url')
            
            record.update({
                'default_account_id': default_account.get('id'),
                'default_account_type': default_account.get('accountType'),
                'default_account_type_name': default_account.get('accountTypeName'),
                'default_location': default_account.get('location'),
                'default_location_name': default_account.get('locationName'),
                'default_province': default_account.get('province'),
                'default_province_name': default_account.get('provinceName'),
                'default_city': default_account.get('city'),
                'default_city_name': default_account.get('cityName'),
                'default_bank_code': default_account.get('bankCode'),
                'default_bank_name': default_account.get('bankName'),
                'default_branch_code': default_account.get('branchCode'),
                'default_branch_name': default_account.get('branchName'),
                'default_bank_account': default_account.get('bankAccount'),
                'default_bank_account_name': default_account.get('bankAccountName'),
                'default_bank_account_id_num': default_account.get('bankAccountIdNum'),
                # 银行卡正面: bankAccountFileId / bankAccountFileVo.urlOss.url
                'default_bank_card_front': default_account.get('bankAccountFileId'),
                'default_bank_card_front_url': bank_card_front_url,
                # 身份证正面: bankAccountIdCardFileId / bankAccountIdCardFileVo.urlOss.url
                'default_id_card_front': default_account.get('bankAccountIdCardFileId'),
                'default_id_card_front_url': id_card_front_url,
                # 身份证反面: API响应中没有此字段，保留为空
                'default_id_card_back': None,
                'default_id_card_back_url': None,
                'default_account_status': default_account.get('accountStatus'),
                'default_account_status_name': default_account.get('accountStatusName'),
                'default_valid_status': default_account.get('validStatus'),
                'default_payee_legal_person_rel': default_account.get('payeeLegalPersonRel'),
                'default_payee_legal_person_rel_name': default_account.get('payeeLegalPersonRelName'),
                'default_payee_country_code': default_account.get('payeeCountryCode'),
                'default_payee_born_country_code': default_account.get('payeeBornCountryCode'),
                'default_payee_born_country_code_title': default_account.get('payeeBornCountryCodeTitle'),
            })
        
        return self.insert_data([record])

    def get_by_store_username(self, store_username, include_deleted=False):
        session = self.Session()
        try:
            query = session.query(SheinSupplierFinance).filter(
                SheinSupplierFinance.store_username == store_username
            )
            if not include_deleted:
                query = query.filter(SheinSupplierFinance.is_deleted == 0)
            return query.first()
        finally:
            session.close()

    def get_all(self, include_deleted=False):
        session = self.Session()
        try:
            query = session.query(SheinSupplierFinance)
            if not include_deleted:
                query = query.filter(SheinSupplierFinance.is_deleted == 0)
            return query.all()
        finally:
            session.close()


# ==================== 便捷函数 ====================

_company_manager = None
_finance_manager = None


def get_company_manager(database_url):
    global _company_manager
    if _company_manager is None:
        _company_manager = SheinSupplierCompanyManager(database_url)
    return _company_manager


def get_finance_manager(database_url):
    global _finance_manager
    if _finance_manager is None:
        _finance_manager = SheinSupplierFinanceManager(database_url)
    return _finance_manager


if __name__ == '__main__':
    # 测试代码
    database_url = "mysql+pymysql://root:123wyk@47.83.212.3:3306/lz"

    # 创建公司信息表
    company_manager = SheinSupplierCompanyManager(database_url)
    company_manager.create_table()
    
    # 创建财务信息表
    finance_manager = SheinSupplierFinanceManager(database_url)
    finance_manager.create_table()
    
    print("表创建完成")
