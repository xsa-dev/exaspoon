use schemars::JsonSchema;
use serde::{Deserialize, Serialize};
use std::fmt;

#[derive(Debug, Clone, Copy, Serialize, Deserialize, JsonSchema, PartialEq)]
#[serde(rename_all = "snake_case")]
pub enum TransactionDirection {
    Income,
    Expense,
    Transfer,
}

impl TransactionDirection {
    pub fn as_ref(&self) -> &'static str {
        match self {
            Self::Income => "income",
            Self::Expense => "expense",
            Self::Transfer => "transfer",
        }
    }
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, JsonSchema, PartialEq)]
#[serde(rename_all = "snake_case")]
pub enum CategoryKind {
    Income,
    Expense,
    Transfer,
}

impl CategoryKind {
    pub fn as_ref(&self) -> &'static str {
        match self {
            Self::Income => "income",
            Self::Expense => "expense",
            Self::Transfer => "transfer",
        }
    }
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, JsonSchema, PartialEq)]
#[serde(rename_all = "snake_case")]
pub enum AccountType {
    Onchain,
    Offchain,
}

impl AccountType {
    pub fn as_ref(&self) -> &'static str {
        match self {
            Self::Onchain => "onchain",
            Self::Offchain => "offchain",
        }
    }
}

impl fmt::Display for AccountType {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.as_ref())
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema)]
pub struct CreateTransactionInput {
    pub account_id: String,
    pub amount: f64,
    pub currency: String,
    pub direction: TransactionDirection,
    pub occurred_at: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub description: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub raw_source: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema)]
pub struct SearchSimilarInput {
    pub query: String,
    #[serde(default)]
    pub limit: Option<u32>,
}

#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema)]
pub struct UpsertCategoryInput {
    pub name: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub kind: Option<CategoryKind>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub description: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema)]
pub struct ListAccountsInput {
    #[serde(rename = "type", skip_serializing_if = "Option::is_none")]
    pub r#type: Option<AccountType>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub search: Option<String>,
}

impl Default for ListAccountsInput {
    fn default() -> Self {
        Self {
            r#type: None,
            search: None,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema)]
pub struct UpsertAccountInput {
    pub name: String,
    #[serde(rename = "type")]
    pub r#type: AccountType,
    pub currency: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub network: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub institution: Option<String>,
}
