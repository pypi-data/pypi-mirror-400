use crate::reverse::rsa_encryption::encrypt_payload;

pub struct Compressor {
    pub(crate) charset: String,
    pub(crate) rand_bytes: [u8; 128],
}

impl Compressor {
    pub fn new(charset: String) -> Self {
        let rand_bytes = & rand::random::<[u8; 128]>();

        Self { charset, rand_bytes: *rand_bytes }
    }

    pub fn compress(&self, input: &str) -> String {
        let rand_bytes = & rand::random::<[u8; 128]>();
        
        encrypt_payload(input, &self.charset, &mut rand_bytes.clone())
    }
}
